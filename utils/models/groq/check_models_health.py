# python utils/models/groq/check_models_health.py

import os
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def check_groq_health(model_list):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ Error: GROQ_API_KEY not found.")
        return

    client = Groq(api_key=api_key)
    results = []

    print(f"🧐 Validating {len(model_list)} Groq models via Canary Calls...\n")

    for model_id in model_list:
        print(f"🔎 Testing: {model_id}")
        try:
            start_time = time.time()
            # Perform a minimal 1-token request
            client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=1
            )
            latency = round((time.time() - start_time) * 1000, 2)
            results.append((model_id, f"✅ READY ({latency}ms)"))
            print(f"   🚀 SUCCESS: Responding at {latency}ms")
        
        except Exception as e:
            err_msg = str(e).lower()
            if "429" in err_msg:
                status = "⏳ 429 RATE LIMIT"
            elif "413" in err_msg:
                status = "📏 413 TOO LARGE"
            else:
                status = "❌ OFFLINE/ERROR"
            print(f"   {status}")
            results.append((model_id, status))
        
        # Groq free tier is sensitive; small sleep prevents self-imposed 429
        time.sleep(1.0)

    # Final Summary Table
    print("\n" + "="*70)
    print(f"{'MODEL ID':<45} | {'HEALTH STATUS'}")
    print("-" * 70)
    for mid, health in results:
        print(f"{mid:<45} | {health}")
    print("="*70)

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
    check_groq_health(model_list)
    