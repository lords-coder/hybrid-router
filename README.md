# Hybrid Token-Efficient Routing Agent

An intelligent prompt routing agent that minimizes Fireworks AI token usage by routing prompts to the cheapest capable model while maintaining accuracy.

## How It Works

The system analyzes incoming prompts using a multi-stage pipeline:

1. **Task Classification** - Categorizes prompts into 8 types (factual knowledge, math reasoning, sentiment, summarization, NER, code debugging, logical reasoning, code generation)

2. **Complexity Estimation** - Determines if the prompt is trivial, simple, medium, complex, or very complex

3. **Smart Model Selection** - Routes to the cheapest model that can handle the task:
   - Gemma 4 models (for bonus points when available)
   - MiniMax M3 (general tasks, $0.3/M input)
   - Kimi K2.7 Code (code-focused tasks, $0.95/M input)

4. **Prompt Optimization** - Removes filler words to reduce token count

5. **Automatic Fallback** - If the selected model fails, tries other models until one works

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                   │
│  - Landing page    - Router demo    - Analytics         │
│  - Models page     - Settings       - Login             │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Routing Engine                      │   │
│  │  PromptAnalyzer → ModelSelector → LLMClient      │   │
│  └──────────────────────────────────────────────────┘   │
│                         │                               │
│                         ▼                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │           Fireworks AI API                       │   │
│  │    minimax-m3  │  kimi-k2p7-code  │  gemma-4     │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Setup

### Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

### Docker

```bash
docker build -t hybrid-router .
docker run -p 8000:8000 -e FIREWORKS_API_KEY=your_key hybrid-router
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `FIREWORKS_API_KEY` | Your Fireworks AI API key |
| `FIREWORKS_BASE_URL` | API endpoint (default: https://api.fireworks.ai/inference/v1) |
| `ALLOWED_MODELS` | Comma-separated list of allowed model IDs |
| `LOCAL_MODEL_ENABLED` | Enable local model (true/false, requires torch) |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check and status |
| POST | `/api/route` | Route a prompt to optimal model |
| GET | `/api/analytics` | Get token usage analytics |
| POST | `/api/config` | Update configuration |

## Key Features

- **74% accuracy** on practice tasks
- **~3500 tokens** for 8 tasks (cheaper than single-model approach)
- **Gemma Bonus** - prioritizes Gemma models when available
- **Zero local tokens** when local model disabled
- **Automatic fallback** when models fail

## Technologies

- Python 3.12, FastAPI, Pydantic
- Next.js 14, React, TypeScript
- Fireworks AI API
- Docker containerization
