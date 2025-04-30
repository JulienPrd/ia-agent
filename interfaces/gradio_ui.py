import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import gradio as gr
from agent_core import AgentSession

session = AgentSession(debug=True)

def chat_fn(message, history):
    response = session.ask(message)
    result = response["RESULT"]
    if response["ACTION"] != "NONE":
        action_output = response.get("ACTION_OUTPUT", "Not specified")
        result += f"\nIdentified action: {response['ACTION']} - {action_output}"
    return {"role": "assistant", "content": result}

gr.ChatInterface(
    fn=chat_fn,
    type="messages",
    chatbot=gr.Chatbot(type="messages"),
    title="Your AI Agent",
    description="Ask me a question about Flutter or any other topic."
).launch()