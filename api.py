"""
FastAPI application.
Imports the agent from floki_agent.py and exposes endpoints.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

from floki_agent import run_floki_agent

# -----------------
# FastAPI setup
# -----------------
app = FastAPI(title="Floki AI Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# -----------------
# Request/response
# -----------------
class ChatRequest(BaseModel):
    user_query: str
    chat_history: List[Dict[str, Any]] = []

class ChatResponse(BaseModel):
    floki_response: str
    updated_chat_history: List[Dict[str, Any]]

# -----------------
# Endpoints
# -----------------
@app.get("/")
def root():
    return {"message": "Floki AI Agent is running!"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    response_text, updated_history = await run_floki_agent(
        request.user_query, request.chat_history
    )
    return ChatResponse(
        floki_response=response_text, updated_chat_history=updated_history
    )

# -----------------
# Run server (dev)
# -----------------
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)