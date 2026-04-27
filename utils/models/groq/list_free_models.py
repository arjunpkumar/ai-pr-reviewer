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
    """Displays the model list with context and dynamic alignment."""
    if not models:
        print("No Groq models found or an error occurred.")
        return

    # 1. Prepare data and find max widths for alignment
    table_data = []
    max_id_len = 8  # 'MODEL ID'
    max_owner_len = 8  # 'OWNED BY'

    for model in models:
        m_id = model.id
        owner = model.owned_by
        status = "ACTIVE" if model.active else "INACTIVE"
        
        # Groq doesn't always expose context in list(), so we infer:
        context = "N/A" 
        if "70b" in m_id.lower(): context = "128k"
        elif "8b" in m_id.lower(): context = "8k"
        elif "mixtral" in m_id.lower(): context = "32k"

        max_id_len = max(max_id_len, len(m_id))
        max_owner_len = max(max_owner_len, len(owner))
        table_data.append((m_id, owner, context, status))

    # 2. Sort for readability
    table_data.sort(key=lambda x: x[0])

    print(f"\n✨ Found {len(models)} Models on Groq:\n")
    
    # 3. Dynamic Header
    header = f"{'MODEL ID':<{max_id_len + 2}} | {'OWNED BY':<{max_owner_len + 2}} | {'CONTEXT':<10} | {'STATUS'}"
    print(header)
    print("-" * len(header))

    # 4. Print Rows
    for m_id, owner, ctx, status in table_data:
        print(f"{m_id:<{max_id_len + 2}} | {owner:<{max_owner_len + 2}} | {ctx:<10} | {status}")

def save_models_to_file(models):
    """Saves only the model IDs to a text file in the script's directory."""
    if not models:
        return
    
    # Get the directory where the script file is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "free_models.txt")
    
    # CORRECTION: Access .id directly (Groq models are objects, not dicts)
    model_ids = sorted([model.id for model in models])
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            for m_id in model_ids:
                f.write(f"{m_id}\n")
        print(f"\n💾 Saved {len(model_ids)} model IDs to: {file_path}")
    except Exception as e:
        print(f"❌ Failed to save file: {e}")

if __name__ == "__main__":
    groq_models = fetch_groq_models()
    display_models(groq_models)
    save_models_to_file(groq_models)