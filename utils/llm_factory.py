import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# OpenRouter Configuration
OPENROUTER_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Use 'openai/gpt-4o' or 'anthropic/claude-3.5-sonnet' etc.
SMART_MODEL_NAME = "nvidia/nemotron-3-super-120b-a12b:free" 
FAST_MODEL_NAME = "meta-llama/llama-3.3-70b-instruct:free" # Or any cheap model on OpenRouter

SMART_MODEL = ChatOpenAI(
    model=SMART_MODEL_NAME,
    openai_api_key=OPENROUTER_API_KEY,
    base_url=OPENROUTER_BASE_URL,
    default_headers={
        "HTTP-Referer": "http://localhost:8080", # OpenRouter likes to know who is calling
        "X-Title": "Flutter AI Reviewer",
    }
)

FAST_MODEL = ChatOpenAI(
    model=FAST_MODEL_NAME,
    openai_api_key=OPENROUTER_API_KEY,
    base_url=OPENROUTER_BASE_URL,
)