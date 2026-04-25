# python utils/models/open_router/check_open_router_health.py

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

if __name__ == "__main__":
    # Add any models from your previous list here to test them
    test_list = ['baidu/qianfan-ocr-fast:free', 'cognitivecomputations/dolphin-mistral-24b-venice-edition:free', 'google/gemma-3-12b-it:free', 'google/gemma-3-27b-it:free', 'google/gemma-3-4b-it:free', 'google/gemma-3n-e2b-it:free', 'google/gemma-3n-e4b-it:free', 'google/gemma-4-26b-a4b-it:free', 'google/gemma-4-31b-it:free', 'google/lyria-3-clip-preview', 'google/lyria-3-pro-preview', 'inclusionai/ling-2.6-1t:free', 'inclusionai/ling-2.6-flash:free', 'liquid/lfm-2.5-1.2b-instruct:free', 'liquid/lfm-2.5-1.2b-thinking:free', 'meta-llama/llama-3.2-3b-instruct:free', 'meta-llama/llama-3.3-70b-instruct:free', 'minimax/minimax-m2.5:free', 'nousresearch/hermes-3-llama-3.1-405b:free', 'nvidia/nemotron-3-nano-30b-a3b:free', 'nvidia/nemotron-3-super-120b-a12b:free', 'nvidia/nemotron-nano-12b-v2-vl:free', 'nvidia/nemotron-nano-9b-v2:free', 'openai/gpt-oss-120b:free', 'openai/gpt-oss-20b:free', 'openrouter/free', 'qwen/qwen3-coder:free', 'qwen/qwen3-next-80b-a3b-instruct:free', 'tencent/hy3-preview:free', 'z-ai/glm-4.5-air:free',]
    check_multiple_models(test_list)
# ✨ Found 30 Free Models on OpenRouter:

# MODEL ID                                                     | CONTEXT      | MODALITY
# --------------------------------------------------------------------------------------
# baidu/qianfan-ocr-fast:free                                  | 65536        | Text Only
# cognitivecomputations/dolphin-mistral-24b-venice-edition:free | 32768        | Text Only
# google/gemma-3-12b-it:free                                   | 32768        | Text+Vision
# google/gemma-3-27b-it:free                                   | 131072       | Text+Vision
# google/gemma-3-4b-it:free                                    | 32768        | Text+Vision
# google/gemma-3n-e2b-it:free                                  | 8192         | Text Only
# google/gemma-3n-e4b-it:free                                  | 8192         | Text Only
# google/gemma-4-26b-a4b-it:free                               | 262144       | Text Only
# google/gemma-4-31b-it:free                                   | 262144       | Text Only
# google/lyria-3-clip-preview                                  | 1048576      | Text Only
# google/lyria-3-pro-preview                                   | 1048576      | Text Only
# inclusionai/ling-2.6-1t:free                                 | 262144       | Text Only
# inclusionai/ling-2.6-flash:free                              | 262144       | Text Only
# liquid/lfm-2.5-1.2b-instruct:free                            | 32768        | Text Only
# liquid/lfm-2.5-1.2b-thinking:free                            | 32768        | Text Only
# meta-llama/llama-3.2-3b-instruct:free                        | 131072       | Text Only
# meta-llama/llama-3.3-70b-instruct:free                       | 65536        | Text Only
# minimax/minimax-m2.5:free                                    | 196608       | Text Only
# nousresearch/hermes-3-llama-3.1-405b:free                    | 131072       | Text Only
# nvidia/nemotron-3-nano-30b-a3b:free                          | 256000       | Text Only
# nvidia/nemotron-3-super-120b-a12b:free                       | 262144       | Text Only
# nvidia/nemotron-nano-12b-v2-vl:free                          | 128000       | Text Only
# nvidia/nemotron-nano-9b-v2:free                              | 128000       | Text Only
# openai/gpt-oss-120b:free                                     | 131072       | Text Only
# openai/gpt-oss-20b:free                                      | 131072       | Text Only
# openrouter/free                                              | 200000       | Text Only
# qwen/qwen3-coder:free                                        | 262000       | Text Only
# qwen/qwen3-next-80b-a3b-instruct:free                        | 262144       | Text Only
# tencent/hy3-preview:free                                     | 262144       | Text Only
# z-ai/glm-4.5-air:free                                        | 131072       | Text Only