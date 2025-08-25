
======================================
app.py
import os
import asyncio
from typing import List, Dict, Any
from dotenv import load_dotenv  # <-- fixed import

from agents import (
    Agent,
    Runner,
    OpenAIChatCompletionsModel,
    function_tool,
    set_tracing_disabled,
)
from openai import AsyncOpenAI

# -----------------
# Load environment variables first
# -----------------
load_dotenv()

# -----------------
# Gemini API config
# -----------------
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
API_KEY = os.getenv("GEMINI_API_KEY") or "YOUR_GEMINI_KEY_HERE"
MODEL_NAME = "gemini-2.0-flash"

if not API_KEY or API_KEY == "YOUR_GEMINI_KEY_HERE":
    raise ValueError("GEMINI_API_KEY is missing! Set it in your .env file.")

set_tracing_disabled(True)

client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)

model_ai = OpenAIChatCompletionsModel(
    model=MODEL_NAME,
    openai_client=client,
)


# ---------------
# FundedFlow tools
# ---------------
@function_tool
def get_fundedflow_module_info(module_name: str) -> str:
    """
    Provides detailed information about a specific FundedFlow module.
    """
    module_name_lower = module_name.lower()

    modules_data = {
        "7-day reset challenge": {
            "purpose": "Hey there! The **7-Day Reset Challenge** is super important. It's designed to help you bounce back after a tough trading patch. Think of it as hitting the 'reset' button on your mindset. We're all about turning those setbacks into awesome comebacks!",
            "how_to_use": "It's really straightforward! When you start, you'll see just Day 1. No peeking ahead, okay? Each day gives you a cool mindset prompt (could be text, a quote, or even a video!) and a spot for you to write down your thoughts – that's your reflection. Once you finish that, boom! Day 2 unlocks. There's a little progress bar to cheer you on. Just keep coming back daily, and you'll build incredible mental strength!",
            "benefits": "This challenge is a game-changer for your mental game. It helps you reset your focus, rebuild your discipline, and get that strong mindset back. By taking it one day at a time, you build consistency without feeling overwhelmed. You got this!"
        },
        "risk tracker": {
            "purpose": "Alright, let's talk about the **Risk Tracker**! This module is all about helping you become a pro at managing risk and truly understanding your trading habits. It's not just about numbers; it's about making smarter choices!",
            "how_to_use": "You'll use a 'Trade Entry Form' to jot down details for each trade. Things like what you traded (the instrument), your entry and exit prices, how much you risked (your account risk percentage), and what you expected to gain (your Reward:Risk ratio). The cool part? You also tag your emotions during the trade! Then, the dashboard lights up with awesome visuals: charts showing your daily drawdown, how your R:R changes over time, and even a heatmap of your emotions. You can filter all this by date, emotion, or instrument to really zoom in on your patterns. Super helpful!",
            "benefits": "This tracker gives you crystal-clear visuals of your risk habits. You'll quickly see if you're risking too much, understand your R:R better, and discover how your feelings affect your trades. It's absolutely key for building that consistent, disciplined trading style. No more guessing!"
        },
        "trading journal": {
            "purpose": "The **Trading Journal** is your personal secret weapon for self-awareness! This one is less about the cold, hard numbers and more about your feelings and thoughts. It helps you log your trading behavior, track those emotional ups and downs, and review your decisions. It's all about building consistency and understanding *you* better.",
            "how_to_use": "It's like your personal diary for trading! You'll fill out a form with the trade date, what you traded, if it was a Long or Short, your setup name (like 'Breakout' or 'Pullback'), prices, and your profit/loss. The best part? You record your emotion *before* you entered the trade and *after* you exited, plus your confidence level (1-5 stars). There's also a 'What I learned' section – super important! You can even add screenshots. All your entries show up in a 'Journal Feed' that you can filter. And get this: there's a 'Weekly Review Screen' that gives you a quick summary of your trades, common emotions, and even prompts you to reflect on what you'll do differently next week. How cool is that?",
            "benefits": "This journal really helps you dig deep into your trading psychology. You'll understand the emotional impact of your trades, spot your personal patterns, and constantly learn and grow through your own reflections. It's a powerful way to improve your decision-making and stay consistent."
        },
        "recovery plan generator": {
            "purpose": "Okay, the **Recovery Plan Generator** is like having your own personal trading coach right here! Its job is to look at *all* your trading data from the Reset, Journal, Risk Tracker, and Simulator, and then create a super personalized improvement plan just for you. It's your roadmap to getting ready for your next big challenge!",
            "how_to_use": "It's pretty smart! The system automatically pulls in all your info – like if you skipped any Reset days, what you wrote in your journal, your risk numbers, and why you might have struggled in the simulator. Then, it cooks up a 'Recovery Plan' report. This report will clearly show you 3 key areas you need to focus on (like 'Emotional discipline' or 'Over-risking'). It explains *why* these areas are important for *you*, gives you clear 'Next Steps' with daily practices, and even links to helpful resources. You can download it as a PDF, and you can even regenerate it anytime you've added new data. It's always adapting to help you!",
            "benefits": "This plan is totally tailor-made for you, directly tackling your specific weaknesses. It takes all your past performance and turns it into actionable steps. This is how you build a rock-solid foundation for future trading success. No more guessing what to work on!"
        },
        "loyalty program": {
            "purpose": "Alright, listen up! The **Loyalty Program** is your very own trader XP (Experience Points) system right here in FundedFlow! It's all about rewarding you for being smart and disciplined. Imagine getting points for *not* overtrading – pretty sweet, right?",
            "how_to_use": "You earn points for doing all the good stuff in the app! Things like finishing a day in the 7-Day Reset (+10 points), logging a trade with all those important emotion tags (+5 points), reviewing your trades with notes (+10 points), sticking to a risk rule for 3 days straight (+15 points), crushing a full simulation (+25 points), and generating your Recovery Plan (+10 points). As you rack up XP, you'll level up (we've got cool titles like 'Tilt Survivor' and 'Risk Samurai'!) and earn special badges for hitting milestones. And guess what? These points can even unlock awesome rewards like extra simulator credits or one-on-one audit sessions! How cool is that?",
            "benefits": "This program makes your trading journey fun and rewarding! It motivates you to consistently use the tools that build great habits, which means less emotional trading and more consistency. It's all about celebrating your growth, not just your profits!"
        },
        "trading simulator": {
            "purpose": "Okay, the **Trading Simulator** is your ultimate playground for practice! It's a super realistic environment where you can practice for those big prop firm challenges (like FTMO, MFF, The Funded Trader, The5ers) without risking a single penny of real money. It's perfect for honing your risk management, testing out your strategies, and truly seeing if you're ready – or if those emotions are still getting in the way!",
            "how_to_use": "It's easy to get started! Just hit 'Start New Sim,' set your initial balance (maybe $10,000 to start?), pick a risk profile (aggressive, balanced, or conservative), and define your rules like daily loss limits, max total drawdown, your profit target, and how long you want the sim to run. Then, you just log each trade within the simulator. It keeps track of your profit/loss, catches any rule violations, monitors how often you trade, your lot sizing, and even those pre/post emotion tags. When you're done, you get a detailed pass/fail report! It breaks down *why* you failed (if you did), your emotional patterns, any trading errors (like revenge trades), and even gives you suggestions from me, Floki! You can retry as many times as you need and adjust the rules to keep learning.",
            "benefits": "This is a zero-risk zone to sharpen your skills, test your strategies under real-world pressure, and build serious confidence. It's designed to help you avoid those expensive mistakes in real funded challenges by letting you learn and adapt in a safe, simulated environment. Practice makes perfect, trader!"
        }
    }

    if module_name_lower in modules_data:
        data = modules_data[module_name_lower]
        return (
            f"Alright, let's talk about the **{module_name}**!\n\n"
            f"**Purpose:** {data['purpose']}\n\n"
            f"**How to use it:** {data['how_to_use']}\n\n"
            f"**Why it helps you:** {data['benefits']}"
        )
    else:
        return (
            "Hmm, I can only provide information about FundedFlow's modules: "
            "'7-Day Reset Challenge', 'Risk Tracker', 'Trading Journal', "
            "'Recovery Plan Generator', 'Loyalty Program', or 'Trading Simulator'. "
            "Which one would you like to know about?"
        )


@function_tool
def get_fundedflow_overview() -> str:
    return (
        "Hey there, future funded trader! FundedFlow is your ultimate dashboard, "
        "built just for you. It's designed to help you master your mindset, "
        "build super disciplined risk habits, and get you fully prepared for "
        "those real prop firm challenges. Think of it as your personal coach "
        "and training ground, all in one place! We've got different modules that "
        "work together to transform your trading journey, focusing on making you "
        "more self-aware, consistent, and strategically brilliant. Our goal? "
        "To help you get funded and stay funded! Let's do this! 🚀"
    )


# -----------------
# Singleton agent
# -----------------
agent = Agent(
    name="Floki AI Agent",
    instructions="""
You are Floki — a friendly, super-encouraging AI onboarding & support bot for FundedFlow.
FundedFlow is a private dashboard that helps traders reset mindset, improve risk habits,
and simulate challenges.

Be informal, concise, and chat like a friend. Use emojis and exclamation points.
Guide traders gently to the right tool or next action. Never judge — always cheer them on.

Explain FundedFlow’s modules in detail when asked, and always relate general trading
questions back to how FundedFlow’s tools can help.

If the question is unrelated to trading or FundedFlow, politely say you can only help
with trading topics.

Remember: keep it short, fun, and helpful! 💪
""",
    model=OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client),
    tools=[get_fundedflow_module_info, get_fundedflow_overview],
)

# -------------------------------------------------
# Public helper: run the agent on a message/history
# -------------------------------------------------
async def run_floki_agent(
    user_query: str, chat_history: List[Dict[str, Any]]
) -> tuple[str, List[Dict[str, Any]]]:
    """
    Returns (response_text, updated_history)
    """
    history = chat_history + [{"role": "user", "content": user_query}]
    result = await Runner.run(agent, history)
    updated_history = history + [{"role": "model", "content": result.final_output}]
    return result.final_output, updated_history



asyncio.run(run_floki_agent())

================================================================================================
# -- index.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Floki AI Chatbot</title>
    <!-- Tailwind CSS CDN for easy styling -->
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap');
        body {
            font-family: 'Inter', sans-serif;
        }
    </style>
</head>
<body class="bg-slate-900 text-white flex items-center justify-center min-h-screen p-4">
    <div class="flex flex-col w-full max-w-2xl bg-slate-800 rounded-xl shadow-lg h-[90vh]">
        
        <!-- Header -->
        <header class="p-6 border-b border-slate-700">
            <h1 class="text-3xl font-bold text-teal-400">Floki AI Chatbot</h1>
            <p class="text-slate-400 mt-1">Chat with Floki, your friendly FundedFlow assistant!</p>
        </header>

        <!-- Chat messages container -->
        <main id="chat-box" class="flex-grow p-6 overflow-y-auto space-y-4">
            <!-- Initial welcome message from Floki -->
            <div class="flex justify-start">
                <div class="bg-slate-700 text-white p-4 rounded-xl max-w-sm">
                    <p class="font-medium text-teal-300">Floki</p>
                    <p class="mt-1">Hey there, future funded trader! How can I help you today? I'm here to answer questions about FundedFlow's modules and general trading concepts. Let's get started! 💪</p>
                </div>
            </div>
        </main>

        <!-- Input and send button -->
        <div class="p-4 border-t border-slate-700 flex items-center gap-2">
            <input type="text" id="user-input" placeholder="Ask Floki a question..."
                   class="flex-grow p-3 rounded-lg bg-slate-700 border-2 border-slate-600 text-white placeholder-slate-400 focus:outline-none focus:border-teal-400 transition-colors">
            <button id="send-button"
                    class="bg-teal-500 text-white font-bold p-3 rounded-lg hover:bg-teal-400 transition-colors shadow-md">
                Send
            </button>
        </div>

    </div>

    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const chatBox = document.getElementById('chat-box');
            const userInput = document.getElementById('user-input');
            const sendButton = document.getElementById('send-button');

            // IMPORTANT: This API URL must match the host and port of your FastAPI server
            const API_URL = "http://127.0.0.1:8000/chat";
            let chatHistory = []; // Initialize empty chat history

            /**
             * Appends a message to the chat box.
             * @param {string} sender - The sender of the message ('user' or 'floki').
             * @param {string} text - The content of the message.
             */
            function appendMessage(sender, text) {
                const messageDiv = document.createElement('div');
                const isUser = sender === 'user';
                messageDiv.className = `flex ${isUser ? 'justify-end' : 'justify-start'}`;

                const messageContent = document.createElement('div');
                messageContent.className = `p-4 rounded-xl max-w-sm ${isUser ? 'bg-indigo-600 text-white' : 'bg-slate-700 text-white'}`;
                
                if (!isUser) {
                    const senderName = document.createElement('p');
                    senderName.className = 'font-medium text-teal-300';
                    senderName.textContent = 'Floki';
                    messageContent.appendChild(senderName);
                }

                const messageText = document.createElement('p');
                messageText.className = isUser ? '' : 'mt-1';
                messageText.innerHTML = text.replace(/\n/g, '<br>'); // Handle newlines
                
                messageContent.appendChild(messageText);
                messageDiv.appendChild(messageContent);
                chatBox.appendChild(messageDiv);
                
                // Scroll to the bottom of the chat box
                chatBox.scrollTop = chatBox.scrollHeight;
            }

            /**
             * Handles sending a message to the Floki API.
             */
            async function sendMessage() {
                const userQuery = userInput.value.trim();
                if (!userQuery) return;

                // Display user message immediately
                appendMessage('user', userQuery);
                userInput.value = ''; // Clear the input field

                try {
                    const response = await fetch(API_URL, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            user_query: userQuery,
                            chat_history: chatHistory
                        })
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const data = await response.json();
                    
                    // Display Floki's response
                    appendMessage('floki', data.floki_response);
                    
                    // Update chat history for the next turn
                    chatHistory = data.updated_chat_history;

                } catch (error) {
                    console.error('Error:', error);
                    appendMessage('floki', "Oops! It looks like I'm having trouble connecting to the server. Please make sure the FastAPI server is running. 🤔");
                }
            }

            // Event listener for the Send button
            sendButton.addEventListener('click', sendMessage);

            // Event listener for the Enter key on the input field
            userInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        });
    </script>
</body>
</html>
=======================================================================