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
    raise ValueError("❌ GEMINI_API_KEY missing in .env file!")

MODEL_NAME = "gemini-2.0-flash"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
client = AsyncOpenAI(base_url=BASE_URL, api_key=GEMINI_API_KEY)
set_tracing_disabled(disabled=True)

# -----------------
# FundedFlow Modules
# -----------------
MODULES_DATA = {
    "7-day reset challenge": {
        "purpose": "Helps reset mindset after tough trading patches 🌟",
        "how_to_use": "Follow daily prompts for 7 days 📝",
        "benefits": "Builds mental strength & focus 💪",
    },
    "risk tracker": {
        "purpose": "Track risk habits & trading patterns 📊",
        "how_to_use": "Log trades, emotions & analyze 🔍",
        "benefits": "Improves discipline & consistency ✅",
    },
    "trading journal": {
        "purpose": "Reflect on trades 🧠",
        "how_to_use": "Log trades & review patterns 📖",
        "benefits": "Boosts decision-making & self-awareness 🔥",
    },
    "recovery plan generator": {
        "purpose": "Create personalized improvement plans 🛠️",
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

# -----------------
# Tools
# -----------------
@function_tool
def get_fundedflow_module_info(module_name: str) -> str:
    module = MODULES_DATA.get(module_name.lower())
    if not module:
        return f"I only know these modules: {', '.join(MODULES_DATA.keys())}. Pick one! 🤔"
    return (
        f"**{module_name.title()}**\n"
        f"✨ Purpose: {module['purpose']}\n"
        f"📝 How to use: {module['how_to_use']}\n"
        f"💡 Benefits: {module['benefits']}"
    )

@function_tool
def get_fundedflow_overview() -> str:
    return (
        "🌟 FundedFlow is your all-in-one trader dashboard.\n"
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
    return "📚 Modules available: " + ", ".join(MODULES_DATA.keys())

# -----------------
# Agent
# -----------------
agent = Agent(
    name="Floki AI Agent",
    instructions=(
        "You are Floki 🤖🎉, friendly and encouraging!\n"
        "❌ ONLY answer questions about FundedFlow modules or the fundedflow.app website.\n"
        "❌ Do NOT answer anything else.\n"
        "✅ Tools:\n"
        "  • get_fundedflow_module_info → module-specific info\n"
        "  • get_fundedflow_overview → general overview\n"
        "  • list_fundedflow_modules → list modules\n"
        "🌟 Always use emojis & short, friendly messages."
    ),
    model=OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client),
    tools=[get_fundedflow_module_info, get_fundedflow_overview, list_fundedflow_modules],
)

# -----------------
# Runner
# -----------------
async def run_floki_agent(user_query: str) -> str:
    # Call Runner.run without chat_history
    result = await Runner.run(agent, user_query)
    return result.final_output

# -----------------
# Terminal entry
# -----------------
if __name__ == "__main__":
    async def main():
        print("Welcome! I’m Floki, your FundedFlow AI Assistant 🤖🚀")
        print("Ask me about FundedFlow modules, overviews, or how things work!")
        print("Type 'exit' anytime to quit.\n")
        
        while True:
            user_query = input("You: ")
            if user_query.lower() in ["exit", "quit"]:
                print("Bye! 👋")
                break
            response = await run_floki_agent(user_query)
            print(f"Floki: {response}\n")
    asyncio.run(main())

