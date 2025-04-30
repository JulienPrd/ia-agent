import json
import os
import re
import ast
import uuid
import difflib
import logging

from dotenv import load_dotenv
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import TextLoader
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.documents import Document
from character import generate_agent_description

load_dotenv()

with open('character.env.json', 'r') as file:
    agent_profile = json.load(file)

with open("actions_config.json", "r") as file:
    actions_config = json.load(file)

enabled_actions = {key: value for key, value in actions_config.items() if value["enabled"]}
action_labels = list(enabled_actions.keys())

agent_description = generate_agent_description(agent_profile)
project_path = os.getenv("PROJECT_PATH")
os.makedirs("cache", exist_ok=True)

class AgentSession:
    def __init__(self, session_id=None, debug=False, summary_update_threshold=1):
        self.session_id = session_id or str(uuid.uuid4())
        self.history = ChatMessageHistory()
        self.summary_update_threshold = summary_update_threshold
        self.summary_file = os.path.join("cache", f"{self.session_id}_summary.txt")
        self.summary = self._load_summary()
        self.qa_chain = self._build_chain()
        self.debug = debug

    def _log(self, message):
        if self.debug:
            print(f"[LOG] {message}")

    def _load_summary(self):
        if os.path.exists(self.summary_file):
            with open(self.summary_file, "r") as f:
                summary = f.read()
                self._log(f"Loaded summary for session {self.session_id}: {summary}")
                return summary
        return ""

    def _append_to_summary(self, new_content):
        with open(self.summary_file, "a") as f:
            f.write("\n" + new_content.strip())
        self._log(f"Appended to summary: {new_content.strip()}")

    def _overwrite_summary(self, new_content):
        with open(self.summary_file, "w") as f:
            f.write(new_content.strip())
        self._log(f"Saved compressed summary: {new_content.strip()}")

    def _build_chain(self):
        documents = []
        for root, _, files in os.walk(project_path):
            for file in files:
                if file.endswith(".dart"):
                    documents.extend(TextLoader(os.path.join(root, file)).load())

        embedding = OpenAIEmbeddings()
        db = FAISS.from_documents(documents, embedding)
        llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")

        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                agent_description +
                "\n\nYou have access to a summary of the user's personal facts. Use it to answer questions about the user, such as their name, location, job, or preferences. Always try to reuse facts from the summary if relevant.\n\nSummary: {summary}"
            ),
            SystemMessagePromptTemplate.from_template("Context: {context}"),
            SystemMessagePromptTemplate.from_template("Summary: {summary}"),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template(
                "User input: {input}\n"
                "You are an AI assistant specialized in helping users with Flutter development. You support multiple languages, but you should process and classify questions in English internally.\n"
                "Analyze the question and classify it into one of these two categories:\n"
                "- \"REQUEST_ACTION\": The user is asking to perform an action/order/operation. You **must** assign an action from the predefined list.\n"
                "- \"GENERAL_DISCUSSION\": The user is simply asking for general information, and **no action is required**.\n"
                "\n"
                "⚠️ IMPORTANT: If the intent is \"REQUEST_ACTION\", you **must** assign one of the following actions based on the user's intent:\n"
                "- " + "\n- ".join([f"{action} → {details['triggers'][0]}" for action, details in enabled_actions.items()]) + "\n"
                "\n"
                "⚠️ RULES:\n"
                "- You must respond with the user preffred language: " + agent_profile.get("language", "English") + ".\n"
                "- If the intent is \"REQUEST_ACTION\", choose the most appropriate \"ACTION\" from the list based on the user's request.\n"
                "- If the user is just asking a general question (e.g., \"What is Flutter?\"), classify as \"GENERAL_DISCUSSION\" and set \"ACTION\" to \"NONE\".\n"
                "- If the intent is \"REQUEST_ACTION\", your response **must** explicitly mention that the action has been initiated"
                "- If the intent is \"GENERAL_DISCUSSION\", respond normally to the user"
                "- The response **must** be in valid JSON format and contain only the following fields:\n"
                "```json\n"
                "{{\n"
                '  "RESULT": "<your detailed response, mentioning the output format>",\n'
                '  "INTENT": "<REQUEST_ACTION or GENERAL_DISCUSSION>",\n'
                '  "ACTION": "<one of the following values: ' + ", ".join(action_labels) + '>"\n'
                '  "ACTION_OUTPUT": "<if the ACTION field is not NONE, specify the associated result: ' + ", ".join([actions_config[label]['output'] for label in action_labels]) + '>"\n'
                "}}\n"
                "If intent is \"GENERAL_DISCUSSION\", set \"ACTION\" to \"NONE\".\n"
                "Ensure the response is a valid JSON and contains no extra text."
            )
        ])

        combine_docs_chain = create_stuff_documents_chain(llm, prompt)
        qa_chain_raw = create_retrieval_chain(db.as_retriever(), combine_docs_chain)

        return RunnableWithMessageHistory(
            qa_chain_raw,
            lambda _: self.history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer"
        )

    def _safe_parse_json(self, text):
        text = text.strip()
        if text.startswith("```json") and text.endswith("```"):
            text = re.sub(r"^```json\n?|\n?```$", "", text)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            try:
                evaluated = ast.literal_eval(text)
                if isinstance(evaluated, dict):
                    return evaluated
            except Exception:
                pass
        try:
            cleaned = text.replace('"', '"').replace("\\n", "\n")
            return json.loads(cleaned)
        except json.JSONDecodeError:
            self._log("JSON parsing failed")
            self._log(f"Raw content: {text}")
            return None

    def _determine_action(self, question, intent):
        if intent == "GENERAL_DISCUSSION":
            return "NONE"
        question_lower = question.lower().strip()
        best_match = None
        best_ratio = 0.0
        for action, details in enabled_actions.items():
            for trigger in details["triggers"]:
                similarity = difflib.SequenceMatcher(None, question_lower, trigger.lower()).ratio()
                if similarity > best_ratio:
                    best_ratio = similarity
                    best_match = action
        return best_match if best_match and best_ratio > 0.5 else "NONE"

    def ask(self, question):
        self._log(f"Received question: {question}")
        response = self.qa_chain.invoke(
            {"input": question, "summary": self.summary},
            config={"configurable": {"session_id": self.session_id}}
        )

        result_text = response.get("answer", "").strip()
        self._log(f"Raw response: {result_text}")

        parsed = self._safe_parse_json(result_text)
        if not parsed:
            self._log("Failed to parse LLM response as JSON")
            return {
                "RESULT": "Error: cannot parse the LLM result",
                "INTENT": "GENERAL_DISCUSSION",
                "ACTION": "NONE",
                "ACTION_OUTPUT": "",
                "SESSION_ID": self.session_id
            }

        intent = parsed.get("INTENT", "GENERAL_DISCUSSION")
        result = parsed.get("RESULT", "No response provided.")
        action = parsed.get("ACTION", "NONE")
        action_output = actions_config.get(action, {}).get("output", "") if action != "NONE" else ""

        self._log(f"Determined action: {action}")
        self._log(f"Action output: {action_output}")

        self._append_to_summary(question)

        if intent == "GENERAL_DISCUSSION" and len(question) > self.summary_update_threshold:
            self._log("Triggering summary compression")

            compress_prompt = ChatPromptTemplate.from_template(
                "From the following conversation logs, extract all personal facts about the user (e.g. name, age, location, profession, preferences), and write them as a bullet list of facts. Keep it concise and structured.\n\n{context}"
            )

            summarizer = create_stuff_documents_chain(ChatOpenAI(temperature=0), compress_prompt)

            doc = Document(page_content=self._load_summary())
            compressed_result = summarizer.invoke({"context": [doc]})
            self.summary = compressed_result
            self._overwrite_summary(self.summary)

        return {
            "INTENT": intent,
            "RESULT": result,
            "ACTION": action,
            "ACTION_OUTPUT": action_output,
            "SESSION_ID": self.session_id
        }