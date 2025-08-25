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
