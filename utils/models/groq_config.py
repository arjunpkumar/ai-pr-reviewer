from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv


load_dotenv()


def get_smart_groq_model():
    """
    High-intelligence model (Llama 3.3 70B).
    Best for: Architecture and Test Generation.
    """
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0
    )

def get_fast_groq_model():
    """
    Lightning-fast model (Llama 3 8B).
    Best for: Sanity checks and Style linting.
    """
    return ChatGroq(
        model="llama3-8b-8192",
        temperature=0
    )