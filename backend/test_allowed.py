from dotenv import load_dotenv; load_dotenv(override=True)
import os, httpx

key = os.getenv('FIREWORKS_API_KEY')
url = 'https://api.fireworks.ai/inference/v1/chat/completions'
headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}

models = [
    'minimax-m3',
    'kimi-k2p7-code',
    'gemma-4-31b-it',
    'gemma-4-26b-a4b-it',
    'gemma-4-31b-it-nvfp4',
]

for m in models:
    full = f'accounts/fireworks/models/{m}'
    payload = {'model': full, 'messages': [{'role': 'user', 'content': 'What is 2+2?'}], 'max_tokens': 20}
    with httpx.Client(timeout=30.0) as c:
        r = c.post(url, json=payload, headers=headers)
        if r.status_code == 200:
            data = r.json()
            usage = data.get('usage', {})
            msg = data['choices'][0]['message']
            content = (msg.get('content') or msg.get('reasoning_content') or str(msg))[:80]
            print(f'OK: {m} | tokens: in={usage.get("prompt_tokens")}, out={usage.get("completion_tokens")} | {content}')
        else:
            err = r.json().get('error', {}).get('message', '')[:80]
            print(f'FAIL {r.status_code}: {m} - {err}')
