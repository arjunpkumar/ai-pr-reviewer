# python utils/models/open_router/list_free_models_of_open_router.py

import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def fetch_free_models():
    """
    Fetches the list of models from OpenRouter and filters for those that are free.
    Pricing is checked against the 'prompt' field in the pricing object.
    """
    url = "https://openrouter.ai/api/v1/models"
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment variables.")
        return []

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/ai-pr-reviewer", # Optional
        "X-Title": "PR Reviewer Utility", # Optional
    }

    print("📡 Querying OpenRouter API for available models...")
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json().get('data', [])
        
        # Filter: pricing.prompt == "0" means the model is free to use
        free_models = [
            model for model in data 
            if float(model.get('pricing', {}).get('prompt', 1)) == 0
        ]
        
        return free_models

    except requests.exceptions.RequestException as e:
        print(f"❌ API Request failed: {e}")
        return []

def display_models(models):
    """Displays the model list in a clean, formatted table."""
    if not models:
        print("No free models found or an error occurred.")
        return

    print(f"\n✨ Found {len(models)} Free Models on OpenRouter:\n")
    
    # Table Header
    header = f"{'MODEL ID':<60} | {'CONTEXT':<12} | {'MODALITY'}"
    print(header)
    print("-" * len(header))

    # Sort models by ID for easier reading
    for model in sorted(models, key=lambda x: x['id']):
        model_id = model.get('id', 'N/A')
        context = model.get('context_length', 'N/A')
        # Check if it's text, vision, etc.
        modality = "Text+Vision" if "vision" in str(model.get('description', '')).lower() else "Text Only"
        
        print(f"{model_id:<60} | {context:<12} | {modality}")

if __name__ == "__main__":
    free_models = fetch_free_models()
    display_models(free_models)