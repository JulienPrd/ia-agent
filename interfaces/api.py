import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from pydantic import BaseModel
from agent_core import formulate_response

app = FastAPI()

class Request(BaseModel):
    message: str

@app.post("/api")
def ask(request: Request):
    return formulate_response(request.message)
