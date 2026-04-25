from langchain_groq import ChatGroq
from dotenv import load_dotenv


load_dotenv()

def get_groq_model(model_id: str):
    return ChatGroq(
        model=model_id,
        temperature=0,
    )

def get_smart_groq_model():
    """
    High-intelligence model (Llama 3.3 70B).
    Best for: Architecture and Test Generation.
    """
    return get_groq_model("llama-3.3-70b-versatile")

def get_fast_groq_model():
    """
    Lightning-fast model (Llama 3 8B).
    Best for: Sanity checks and Style linting.
    """
    return get_groq_model("llama3-8b-8192")