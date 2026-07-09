import json
import os
import time
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router
from config.settings import settings

app = FastAPI(
    title="Hybrid Token-Efficient Routing Agent",
    description=(
        "Intelligent AI model routing that picks the cheapest Fireworks AI model "
        "for each task while maximizing accuracy. Local-first strategy for zero tokens."
    ),
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "name": "Hybrid Token-Efficient Routing Agent",
        "version": "2.0.0",
        "status": "running",
        "fireworks_base_url": settings.FIREWORKS_BASE_URL,
        "local_model_enabled": settings.LOCAL_MODEL_ENABLED,
        "local_model": settings.LOCAL_MODEL_NAME,
        "allowed_models": settings.ALLOWED_MODELS,
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


def run_task_mode():
    input_path = os.path.join(settings.INPUT_DIR, "tasks.json")
    output_path = os.path.join(settings.OUTPUT_DIR, "results.json")

    print(f"[TASK RUNNER] Reading tasks from: {input_path}")

    if not os.path.exists(input_path):
        print(f"[TASK RUNNER] No tasks file found at {input_path}")
        return

    with open(input_path, "r") as f:
        tasks = json.load(f)

    print(f"[TASK RUNNER] Loaded {len(tasks)} tasks")

    from router.engine import RoutingEngine
    from router.fireworks_client import llm_client

    engine = RoutingEngine()
    results = []

    for task in tasks:
        task_id = task.get("task_id", "")
        prompt = task.get("prompt", "")
        print(f"[TASK RUNNER] Processing {task_id}: {prompt[:80]}...")

        analysis = engine.route(prompt)
        model_data = analysis["selected_model"]

        selected_model = None
        from config.models import ALL_FIREWORKS_MODELS, LOCAL_MODELS
        for m in ALL_FIREWORKS_MODELS + LOCAL_MODELS:
            if m.name == model_data["name"]:
                selected_model = m
                break
        if not selected_model:
            selected_model = LOCAL_MODELS[0] if settings.LOCAL_MODEL_ENABLED else ALL_FIREWORKS_MODELS[0]

        api_result = llm_client.chat_completion(
            model=selected_model,
            prompt=analysis["optimized_prompt"],
            system_prompt=analysis["system_prompt"],
            temperature=settings.DEFAULT_TEMPERATURE,
            max_tokens=settings.DEFAULT_MAX_TOKENS,
        )

        if not api_result["success"]:
            api_result = llm_client.try_fallback(
                selected_model,
                analysis["optimized_prompt"],
                analysis["system_prompt"],
                settings.DEFAULT_TEMPERATURE,
                settings.DEFAULT_MAX_TOKENS,
            )

        answer = api_result.get("content", "") if api_result.get("success") else ""

        results.append({
            "task_id": task_id,
            "answer": answer,
        })

        print(
            f"[TASK RUNNER] {task_id}: "
            f"model={selected_model.display_name}, "
            f"local={analysis['is_local']}, "
            f"fireworks_tokens={api_result.get('fireworks_tokens', 0)}, "
            f"success={api_result.get('success', False)}"
        )

    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"[TASK RUNNER] Wrote {len(results)} results to: {output_path}")

    total_fw_tokens = sum(
        r.get("fireworks_tokens", 0) for r in results
        if isinstance(r, dict)
    )
    print(f"[TASK RUNNER] Total Fireworks tokens used: {total_fw_tokens}")


if __name__ == "__main__":
    import uvicorn

    if os.path.exists(os.path.join(settings.INPUT_DIR, "tasks.json")):
        print("[TASK RUNNER] Detected tasks.json - running in task mode")
        run_task_mode()
        print("[TASK RUNNER] Task mode complete. Starting web server...")
    else:
        print("[TASK RUNNER] No tasks.json found - starting web server only")

    uvicorn.run(app, host="0.0.0.0", port=8000)
