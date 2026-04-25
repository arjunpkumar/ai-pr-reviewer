# python utils/models/groq/check_groq_health.py

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

if __name__ == "__main__":
    # Common Groq IDs for 2026
    candidates = ['allam-2-7b', 'canopylabs/orpheus-arabic-saudi', 'canopylabs/orpheus-v1-english', 'groq/compound', 'groq/compound-mini', 'llama-3.1-8b-instant', 'llama-3.3-70b-versatile', 'meta-llama/llama-4-scout-17b-16e-instruct', 'meta-llama/llama-prompt-guard-2-22m', 'meta-llama/llama-prompt-guard-2-86m', 'openai/gpt-oss-120b', 'openai/gpt-oss-20b', 'openai/gpt-oss-safeguard-20b', 'qwen/qwen3-32b', 'whisper-large-v3', 'whisper-large-v3-turbo']
    check_groq_health(candidates)

# ✨ Found 16 Models on Groq:

# MODEL ID                                      | OWNED BY        | STATUS
# ------------------------------------------------------------------------
# allam-2-7b                                    | SDAIA           | ACTIVE
# canopylabs/orpheus-arabic-saudi               | Canopy Labs     | ACTIVE
# canopylabs/orpheus-v1-english                 | Canopy Labs     | ACTIVE
# groq/compound                                 | Groq            | ACTIVE
# groq/compound-mini                            | Groq            | ACTIVE
# llama-3.1-8b-instant                          | Meta            | ACTIVE
# llama-3.3-70b-versatile                       | Meta            | ACTIVE
# meta-llama/llama-4-scout-17b-16e-instruct     | Meta            | ACTIVE
# meta-llama/llama-prompt-guard-2-22m           | Meta            | ACTIVE
# meta-llama/llama-prompt-guard-2-86m           | Meta            | ACTIVE
# openai/gpt-oss-120b                           | OpenAI          | ACTIVE
# openai/gpt-oss-20b                            | OpenAI          | ACTIVE
# openai/gpt-oss-safeguard-20b                  | OpenAI          | ACTIVE
# qwen/qwen3-32b                                | Alibaba Cloud   | ACTIVE
# whisper-large-v3                              | OpenAI          | ACTIVE
# whisper-large-v3-turbo                        | OpenAI          | ACTIVE