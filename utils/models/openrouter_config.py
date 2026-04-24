from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Common headers for OpenRouter
OPENROUTER_HEADERS = {
    "HTTP-Referer": "http://localhost:8080",
    "X-Title": "Flutter AI Reviewer",
}

def get_smart_openrouter_model():
    """Top-tier model for Architecture and Test Generation."""
    return ChatOpenAI(
        model="openai/gpt-oss-120b:free", # High reasoning
        base_url="https://openrouter.ai/api/v1",
        default_headers=OPENROUTER_HEADERS,
        temperature=0
    )

def get_fast_openrouter_model():
    """Fast, cheap model for Sanity and Style checks."""
    return ChatOpenAI(
        model="qwen/qwen3-coder:free", 
        base_url="https://openrouter.ai/api/v1",
        default_headers=OPENROUTER_HEADERS,
        temperature=0
    )