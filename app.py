# floki_agent.py
import os
import asyncio
from dotenv import load_dotenv
from typing import List, Dict, Any

from agents import (
    Agent,
    Runner,
    OpenAIChatCompletionsModel,
    function_tool,
    set_tracing_disabled,
)
from openai import AsyncOpenAI

# -----------------
# Load env vars
# -----------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or ""
MODEL_NAME = "gemini-2.0-flash"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY missing! Please set it in your .env file.")

# -----------------
# Async Gemini client
# -----------------
client = AsyncOpenAI(base_url=BASE_URL, api_key=GEMINI_API_KEY)
set_tracing_disabled(disabled=True)

# -----------------
# Tools
# -----------------
MODULES_DATA = {
    "7-day reset challenge": {
        "purpose": "Helps you reset mindset after tough trading patches 🌟",
        "how_to_use": "Follow daily prompts for 7 days 📝",
        "benefits": "Builds mental strength & focus 💪",
    },
    "risk tracker": {
        "purpose": "Track risk habits & trading patterns 📊",
        "how_to_use": "Log trades, emotions & analyze 🔍",
        "benefits": "Improves discipline & consistency ✅",
    },
    "trading journal": {
        "purpose": "Personal reflection on trades 🧠",
        "how_to_use": "Log trades & review patterns 📖",
        "benefits": "Boosts decision-making & self-awareness 🔥",
    },
    "recovery plan generator": {
        "purpose": "Creates custom improvement plan 🛠️",
        "how_to_use": "Generates PDF reports 📄",
        "benefits": "Clear next steps & growth 🚀",
    },
    "loyalty program": {
        "purpose": "Rewards consistent discipline 🎖️",
        "how_to_use": "Earn points & unlock perks",
        "benefits": "Keeps you motivated 🏆",
    },
    "trading simulator": {
        "purpose": "Practice strategies risk-free 🎮",
        "how_to_use": "Simulate trades & analyze results",
        "benefits": "Sharpen skills & confidence 💡",
    },
}


@function_tool
def get_fundedflow_module_info(module_name: str) -> str:
    module = MODULES_DATA.get(module_name.lower())
    if not module:
        return (
            "I only know about: "
            + ", ".join(MODULES_DATA.keys())
            + ". Please pick one 🤔"
        )

    return (
        f"**{module_name.title()}**\n\n"
        f"✨ Purpose: {module['purpose']}\n"
        f"📝 How to use: {module['how_to_use']}\n"
        f"💡 Benefits: {module['benefits']}"
    )


@function_tool
def get_fundedflow_overview() -> str:
    return (
        "🌟 FundedFlow is your all-in-one trader dashboard.\n\n"
        "- Master your **mindset** 🧠\n"
        "- Track your **risk** 📊\n"
        "- Reflect in your **journal** 📖\n"
        "- Recover with **plans** 🛠️\n"
        "- Stay motivated with **loyalty rewards** 🎖️\n"
        "- Sharpen skills in the **simulator** 🎮\n\n"
        "Goal: Get funded & stay funded! 🚀"
    )


@function_tool
def list_fundedflow_modules() -> str:
    return "📚 Available modules: " + ", ".join(MODULES_DATA.keys())


# -----------------
# Floki Agent
# -----------------
agent = Agent(
    name="Floki AI Agent",
    instructions=(
        "You are Floki 🤖🎉\n"
        "- ALWAYS use the correct tool:\n"
        "  • `get_fundedflow_module_info` → when asked about a specific module.\n"
        "  • `get_fundedflow_overview` → when asked for the big picture.\n"
        "  • `list_fundedflow_modules` → when asked what modules exist.\n"
        "- Never invent modules. Always stay friendly & encouraging with emojis!"
    ),
    model=OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client),
    tools=[get_fundedflow_module_info, get_fundedflow_overview, list_fundedflow_modules],
)


# -----------------
# Runner function
# -----------------
async def run_floki_agent(user_query: str) -> str:
    result = await Runner.run(agent, user_query)
    return result.final_output


# -----------------
# Terminal entry
# -----------------
if __name__ == "__main__":

    async def main():
        print("Welcome to Floki AI Agent! Type 'exit' to quit.\n")
        while True:
            user_query = input("You: ")
            if user_query.lower() in ["exit", "quit"]:
                print("Bye! 👋")
                break
            response = await run_floki_agent(user_query)
            print(f"Floki: {response}\n")

    asyncio.run(main())
