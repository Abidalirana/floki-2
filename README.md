mahad-floki/
│
├── .venv/                  # Virtual environment (ignore in git)
├── __pycache__/            # Python cache (ignore in git)
│
├── .env                    # API keys & secrets
├── .gitignore              # Ignore rules (venv, __pycache__, etc.)
├── .python-version         # Python version
├── pyproject.toml          # Project config (dependencies, build)
├── requirements.txt        # Explicit deps (for pip users)
├── uv.lock                 # Lock file for uv
│
├── README.md               # Docs
│
├── app.py                  # App entry (FastAPI/Flask)
├── api.py                  # API routes & endpoints
---- uv lock 


=====================================================================================================================================================================================================================================================================
app.py
# floki_agent.py
import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner, OpenAIChatCompletionsModel, function_tool, set_tracing_disabled
from openai import AsyncOpenAI

# -----------------
# Load environment
# -----------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY missing in .env file!")

MODEL_NAME = "gemini-2.0-flash"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
client = AsyncOpenAI(base_url=BASE_URL, api_key=GEMINI_API_KEY)
set_tracing_disabled(disabled=True)

# -----------------
# Formatter Class
# -----------------
class DotFormatter:
    @staticmethod
    def format_list(items: list[str]) -> str:
        return "\n".join([f". {item}" for item in items])

    @staticmethod
    def format_module(name: str, purpose: str, how_to_use: str, benefits: str) -> str:
        return DotFormatter.format_list([
            f"{name.title()}",
            f"Purpose: {purpose}",
            f"How to use: {how_to_use}",
            f"Benefits: {benefits}"
        ])

# -----------------
# FundedFlow Modules
# -----------------
MODULES_DATA = {
    "7-day reset challenge": {
        "purpose": "Helps reset mindset after tough trading patches",
        "how_to_use": "Follow daily prompts for 7 days",
        "benefits": "Builds mental strength & focus",
    },
    "risk tracker": {
        "purpose": "Track risk habits & trading patterns",
        "how_to_use": "Log trades, emotions & analyze",
        "benefits": "Improves discipline & consistency",
    },
    "trading journal": {
        "purpose": "Reflect on trades",
        "how_to_use": "Log trades & review patterns",
        "benefits": "Boosts decision-making & self-awareness",
    },
    "recovery plan generator": {
        "purpose": "Create personalized improvement plans",
        "how_to_use": "Generates PDF reports",
        "benefits": "Clear next steps & growth",
    },
    "loyalty program": {
        "purpose": "Rewards consistent discipline",
        "how_to_use": "Earn points & unlock perks",
        "benefits": "Keeps you motivated",
    },
    "trading simulator": {
        "purpose": "Practice strategies risk-free",
        "how_to_use": "Simulate trades & analyze results",
        "benefits": "Sharpen skills & confidence",
    },
}

# -----------------
# Tools
# -----------------
@function_tool
def get_fundedflow_module_info(module_name: str) -> str:
    module = MODULES_DATA.get(module_name.lower())
    if not module:
        return DotFormatter.format_list([
            f"I only know these modules: {', '.join(MODULES_DATA.keys())}",
            "Pick one!"
        ])
    return DotFormatter.format_module(
        module_name,
        module["purpose"],
        module["how_to_use"],
        module["benefits"]
    )

@function_tool
def get_fundedflow_overview() -> str:
    return DotFormatter.format_list([
        "FundedFlow is your all-in-one trader dashboard",
        "Master your mindset",
        "Track your risk",
        "Reflect in your journal",
        "Recover with personalized plans",
        "Stay motivated with loyalty rewards",
        "Sharpen skills in the trading simulator",
        "Goal: Help traders get funded AND stay funded long term"
    ])

@function_tool
def list_fundedflow_modules() -> str:
    return DotFormatter.format_list(
        ["Modules available:"] + list(MODULES_DATA.keys())
    )

# -----------------
# Agent
# -----------------
agent = Agent(
    name="Floki AI Agent",
    instructions=(
        "Hey, I’m Floki! I’m your FundedFlow AI Assistant\n\n"
        "Core personality:\n"
        ". Super friendly, short, and encouraging (like a trading buddy)\n"
        ". Never lecture or overwhelm — explain like we’re chatting casually\n"
        ". Always tie answers back to FundedFlow modules or website\n\n"
        "Formatting Rules:\n"
        ". Always format output in dot-style (.)\n"
        ". Keep each point short and clear\n"
        ". Avoid long paragraphs unless absolutely necessary\n\n"
        "Boundaries:\n"
        ". DO NOT answer questions unrelated to trading, FundedFlow, or its modules\n"
        ". If asked something off-topic (e.g., politics, math, coding), politely say you can only help with FundedFlow\n\n"
        "Examples of style:\n"
        ". If asked: 'What’s FundedFlow?' →\n"
        "  . FundedFlow is your all-in-one trader dashboard\n"
        "  . It helps you master mindset, track risk, and crush funded challenges\n"
        "  . Goal: Help you stay funded long-term\n"
        ". If asked: 'Tell me about the journal' →\n"
        "  . The Trading Journal is your reflection space\n"
        "  . Log trades, emotions, and lessons\n"
        "  . Learn from every move\n\n"
        "Golden Rule: Keep it light, positive, actionable, and in dot-style"
    ),
    model=OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client),
    tools=[get_fundedflow_module_info, get_fundedflow_overview, list_fundedflow_modules],
)

# -----------------
# Runner (always fresh, no memory)
# -----------------
async def run_floki_agent(user_query: str) -> str:
    result = await Runner.run(agent, user_query)
    return result.final_output

# -----------------
# Terminal entry
# -----------------
if __name__ == "__main__":
    async def main():
        print(". Welcome! I’m Floki, your FundedFlow AI Assistant")
        print(". Ask me about FundedFlow modules, overviews, or how things work!")
        print(". Type 'exit' anytime to quit.\n")
        
        while True:
            user_query = input("You: ")
            if user_query.lower() in ["exit", "quit"]:
                print(". Bye!")
                break
            response = await run_floki_agent(user_query)
            print(f"Floki:\n{response}\n")
    asyncio.run(main())


==========================================================================================================================================v==============================================================================================================================
02 ----  api.py 

"""
FastAPI application.
Imports the agent from floki_agent.py and exposes endpoints.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

from app import run_floki_agent

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
    response_text = await run_floki_agent(request.user_query)
    return ChatResponse(
        floki_response=response_text,
        updated_chat_history=[]  # always empty
    )

# -----------------
# Run server (dev)
# -----------------
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)

    ==================================================== ==================================================== ==================================================== ==================================================== ==================================================== ====================================================


Here’s the proper requirements.txt:

fastapi>=0.116.1
openai-agents>=0.2.9
python-dotenv>=1.1.1
uvicorn>=0.35.0

Notes:

. No need to add Python version here (that’s handled in pyproject.toml)
. requirements.txt is useful for pip users or deployment platforms (Heroku, Docker, etc.)
. If you want exact locked versions (instead of >=), you can freeze with:

pip freeze > requirements.txt

 ==================================================== ==================================================== ==================================================== ==================================================== ==================================================== ====================================================


try first  
python -m pip freeze > requirements.txt


then is nide copy paste this 

annotated-types==0.7.0
anyio==4.10.0
attrs==25.3.0
certifi==2025.8.3
charset-normalizer==3.4.3
click==8.2.1
colorama==0.4.6
distro==1.9.0
fastapi==0.116.1
griffe==1.12.1
h11==0.16.0
httpcore==1.0.9
httpx==0.28.1
httpx-sse==0.4.1
idna==3.10
jiter==0.10.0
jsonschema==4.25.1
jsonschema-specifications==2025.4.1
mcp==1.13.1
openai==1.101.0
openai-agents==0.2.9
pydantic==2.11.7
pydantic-settings==2.10.1
pydantic_core==2.33.2
python-dotenv==1.1.1
python-multipart==0.0.20
pywin32==311
referencing==0.36.2
requests==2.32.5
rpds-py==0.27.0
sniffio==1.3.1
sse-starlette==3.0.2
starlette==0.47.3
tqdm==4.67.1
types-requests==2.32.4.20250809
typing-inspection==0.4.1
typing_extensions==4.14.1
urllib3==2.5.0
uvicorn==0.35.0


==================================================== ==================================================== ==================================================== ==================================================== ==================================================== ====================================================




