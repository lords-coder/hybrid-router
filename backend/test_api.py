import httpx
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("FIREWORKS_API_KEY", "")
print(f"API Key: {api_key[:15]}..." if api_key else "API Key: EMPTY")

# Try listing models
url = "https://api.fireworks.ai/inference/v1/models"
headers = {"Authorization": f"Bearer {api_key}"}

with httpx.Client(timeout=15.0) as c:
    r = c.get(url, headers=headers)
    print(f"List models status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        models = data.get("data", [])
        print(f"Available models: {len(models)}")
        for m in models[:30]:
            mid = m.get("id", "unknown")
            print(f"  {mid}")
    else:
        print(f"Error: {r.text[:500]}")

# Try a simple chat
print("\n--- Testing chat ---")
chat_url = "https://api.fireworks.ai/inference/v1/chat/completions"

# Try every model variation
test_models = [
    "accounts/fireworks/models/gpt-oss-20b",
    "accounts/fireworks/models/gpt-oss-120b",
    "accounts/fireworks/models/llama-v3p3-70b-instruct",
    "accounts/fireworks/models/llama-v3p1-8b-instruct",
    "accounts/fireworks/models/gemma-2-9b-it",
    "accounts/fireworks/models/mixtral-8x7b-instruct",
    "accounts/fireworks/models/deepseek-v3",
    "accounts/fireworks/models/qwen2-5-0-5b-instruct",
]

for model_id in test_models:
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": "Say hi"}],
        "max_tokens": 5,
    }
    with httpx.Client(timeout=10.0) as c:
        r = c.post(chat_url, json=payload, headers={**headers, "Content-Type": "application/json"})
        if r.status_code == 200:
            print(f"OK: {model_id}")
        else:
            err = r.json().get("error", {}).get("message", "")[:80]
            print(f"FAIL {r.status_code}: {model_id} - {err}")
