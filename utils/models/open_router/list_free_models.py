# python utils/models/open_router/list_free_models.py

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_free_models():
    url = "https://openrouter.ai/api/v1/models"
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("❌ Error: API Key not found.")
        return []

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json().get('data', [])
        
        # Filter for free models
        free_models = [
            model for model in data 
            if float(model.get('pricing', {}).get('prompt', 1)) == 0
        ]
        return free_models
    except Exception as e:
        print(f"❌ API Request failed: {e}")
        return []

def display_models(models):
    if not models:
        print("No free models found.")
        return

    # 1. Prepare the data and find max widths for each column
    table_data = []
    max_id = 8 # Length of 'MODEL ID'
    max_owner = 8 # Length of 'OWNED BY'

    for model in models:
        m_id = model.get('id', 'N/A')
        owner = m_id.split('/')[0].title() if '/' in m_id else "OpenRouter"
        context = str(model.get('context_length', 'N/A'))
        status = "ACTIVE"

        max_id = max(max_id, len(m_id))
        max_owner = max(max_owner, len(owner))
        
        table_data.append((m_id, owner, context, status))

    # 2. Sort data
    table_data.sort(key=lambda x: x[0])

    # 3. Print Header with Dynamic Padding
    print(f"\n✨ Found {len(models)} Free Models on OpenRouter:\n")
    
    # We add 2 extra spaces for padding between columns
    header = f"{'MODEL ID':<{max_id + 2}} | {'OWNED BY':<{max_owner + 2}} | {'CONTEXT':<10} | {'STATUS'}"
    print(header)
    print("-" * len(header))

    # 4. Print Rows
    for m_id, owner, context, status in table_data:
        print(f"{m_id:<{max_id + 2}} | {owner:<{max_owner + 2}} | {context:<10} | {status}")

def save_models_to_file(models):
    """Saves only the model IDs to a text file in the script's directory."""
    if not models:
        return
    
    # Get the directory where the script file is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "free_models.txt")
    
    model_ids = sorted([model.get('id') for model in models])
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            for m_id in model_ids:
                f.write(f"{m_id}\n")
        print(f"\n💾 Saved {len(model_ids)} model IDs to: {file_path}")
    except Exception as e:
        print(f"❌ Failed to save file: {e}")

if __name__ == "__main__":
    free_models = fetch_free_models()
    display_models(free_models)
    save_models_to_file(free_models)