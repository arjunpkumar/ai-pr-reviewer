# python utils/models/groq/list_free_models.py

import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def fetch_groq_models():
    """
    Fetches the list of active models available on Groq.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ Error: GROQ_API_KEY not found in environment variables.")
        return []

    client = Groq(api_key=api_key)
    
    print("📡 Querying Groq API for available models...")
    
    try:
        models = client.models.list()
        return models.data
    except Exception as e:
        print(f"❌ Groq API Request failed: {e}")
        return []

def display_models(models):
    """Displays the model list in a clean, formatted table."""
    if not models:
        print("No Groq models found or an error occurred.")
        return

    print(f"\n✨ Found {len(models)} Models on Groq:\n")
    
    # Table Header
    header = f"{'MODEL ID':<45} | {'OWNED BY':<15} | {'STATUS'}"
    print(header)
    print("-" * len(header))

    # Sort models by ID for easier reading
    for model in sorted(models, key=lambda x: x.id):
        status = "ACTIVE" if model.active else "INACTIVE"
        print(f"{model.id:<45} | {model.owned_by:<15} | {status}")

if __name__ == "__main__":
    groq_models = fetch_groq_models()
    display_models(groq_models)