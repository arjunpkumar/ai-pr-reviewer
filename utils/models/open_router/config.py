from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# Common headers for OpenRouter
OPENROUTER_HEADERS = {
    "HTTP-Referer": "http://localhost:8080",
    "X-Title": "Flutter AI Reviewer",
}

def get_openrouter_model(model_id: str):
    """
    Initializes OpenRouter with JSON mode forced to prevent non-JSON garbage.
    """
    return ChatOpenAI(
        model=model_id,
        default_headers=OPENROUTER_HEADERS,
        base_url="https://openrouter.ai/api/v1",
        temperature=0,
        model_kwargs={"response_format": {"type": "json_object"}}
    )

def get_smart_openrouter_model():
    """Top-tier model for Architecture and Test Generation."""
    return get_openrouter_model("nvidia/nemotron-3-super-120b-a12b:free")

def get_fast_openrouter_model():
    """Fast, cheap model for Sanity and Style checks."""
    return get_openrouter_model("meta-llama/llama-3.3-70b-instruct:free")
