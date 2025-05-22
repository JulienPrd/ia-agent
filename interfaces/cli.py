import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent_core import AgentSession

session = AgentSession(debug=True)
while True:
    question = input(">> ")
    response = session.ask(question)
    print(f"🤖 {response['RESULT']}")
    if response["ACTION"] != "NONE":
        print(f"♻️ Identified action: {response['ACTION']} - {response['ACTION_OUTPUT']}")