# python utils/models/open_router/check_models_health.py

import requests
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()

def check_multiple_models(model_list):
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = "https://openrouter.ai/api/v1"
    
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found.")
        return

    print(f"🧐 Validating {len(model_list)} models...\n")
    results = []

    # 1. Fetch current pricing for all models to confirm $0
    models_resp = requests.get(f"{base_url}/models", headers={"Authorization": f"Bearer {api_key}"})
    all_model_meta = {m['id']: m for m in models_resp.json().get('data', [])} if models_resp.status_code == 200 else {}

    for model_id in model_list:
        print(f"🔎 Checking: {model_id}")
        
        # Step A: Pricing Check
        meta = all_model_meta.get(model_id)
        if not meta:
            print(f"   ⚠️  Model ID not found.")
            results.append((model_id, "MISSING"))
            continue
            
        price = float(meta.get('pricing', {}).get('prompt', 0))
        if price > 0:
            print(f"   ⚠️  NOT FREE (Price: ${price}/1M)")
            results.append((model_id, f"PAID (${price})"))
            continue

        # Step B: Live "Canary" Call
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 1 
        }
        
        try:
            chat_resp = requests.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=10
            )
            
            if chat_resp.status_code == 200:
                print(f"   🚀 SUCCESS: Responding and Free.")
                results.append((model_id, "✅ READY"))
            elif chat_resp.status_code == 402:
                print(f"   🛑 402: Provider limit reached.")
                results.append((model_id, "❌ 402 LIMIT"))
            elif chat_resp.status_code == 429:
                print(f"   ⏳ 429: Rate limited.")
                results.append((model_id, "⏳ 429 LIMIT"))
            else:
                print(f"   ❌ FAILED: {chat_resp.status_code}")
                results.append((model_id, f"ERROR {chat_resp.status_code}"))
        except Exception as e:
            print(f"   💥 CRASH: {str(e)}")
            results.append((model_id, "CRASHED"))

        # Small sleep to prevent self-rate-limiting during checks
        time.sleep(0.5)

    # Final Summary Table
    print("\n" + "="*50)
    print(f"{'MODEL ID':<40} | {'STATUS'}")
    print("-" * 50)
    for mid, status in results:
        print(f"{mid:<40} | {status}")
    print("="*50)

def load_models_from_file():
    """Reads model IDs from free_models.txt in the same directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "free_models.txt")
    
    if not os.path.exists(file_path):
        print(f"❌ Error: {file_path} not found. Run the listing script first.")
        return []
    
    with open(file_path, "r", encoding="utf-8") as f:
        # Strip whitespace and ignore empty lines
        models = [line.strip() for line in f if line.strip()]
    
    return models

if __name__ == "__main__":
    model_list = load_models_from_file()
    check_multiple_models(model_list)
