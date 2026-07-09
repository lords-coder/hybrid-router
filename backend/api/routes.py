from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from router.engine import RoutingEngine
from router.fireworks_client import llm_client
from analytics.store import analytics_store
from config.models import ALL_FIREWORKS_MODELS, LOCAL_MODELS, TaskCategory, ComplexityLevel
from config.settings import settings
import uuid
import time
import os

router = APIRouter()
routing_engine = RoutingEngine()


class PromptRequest(BaseModel):
    prompt: str
    temperature: Optional[float] = 0.3
    max_tokens: Optional[int] = 512


@router.post("/analyze")
async def analyze_prompt(request: PromptRequest):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    analysis = routing_engine.route(request.prompt)
    return {"success": True, "data": analysis}


@router.post("/route")
async def route_and_execute(request: PromptRequest):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    analysis = routing_engine.route(request.prompt)
    model_data = analysis["selected_model"]

    selected_model = None
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
        temperature=request.temperature or settings.DEFAULT_TEMPERATURE,
        max_tokens=request.max_tokens or settings.DEFAULT_MAX_TOKENS,
    )

    if not api_result["success"]:
        api_result = llm_client.try_fallback(
            selected_model,
            analysis["optimized_prompt"],
            analysis["system_prompt"],
            request.temperature or settings.DEFAULT_TEMPERATURE,
            request.max_tokens or settings.DEFAULT_MAX_TOKENS,
        )

    request_id = str(uuid.uuid4())[:8]
    tokens_saved = analysis["optimization"].get("tokens_saved", 0)

    analytics_entry = {
        "id": request_id,
        "prompt": request.prompt[:200],
        "task_type": analysis["task_type"],
        "complexity": analysis["complexity"],
        "reasoning_level": analysis["reasoning_level"],
        "model_name": selected_model.name,
        "model_display": selected_model.display_name,
        "provider": api_result.get("provider", selected_model.provider.value),
        "is_local": analysis["is_local"],
        "input_tokens": api_result.get("input_tokens", 0),
        "output_tokens": api_result.get("output_tokens", 0),
        "total_tokens": api_result.get("total_tokens", 0),
        "fireworks_tokens": api_result.get("fireworks_tokens", 0),
        "tokens_saved": tokens_saved,
        "processing_time_ms": api_result.get("processing_time_ms", 0),
        "confidence": analysis["confidence"],
        "success": api_result.get("success", False),
        "response_preview": (api_result.get("content", "")[:150] if api_result.get("success") else api_result.get("error", "")[:150]),
    }
    analytics_store.log(analytics_entry)

    return {
        "success": api_result.get("success", False),
        "request_id": request_id,
        "analysis": analysis,
        "response": api_result,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }


@router.get("/models")
async def get_models():
    all_models = []
    for m in ALL_FIREWORKS_MODELS:
        allowed = not settings.ALLOWED_MODELS or m.name in settings.ALLOWED_MODELS
        all_models.append({
            "name": m.name,
            "display_name": m.display_name,
            "provider": m.provider.value,
            "capabilities": m.capabilities,
            "reasoning_score": m.reasoning_score,
            "context_length": m.context_length,
            "max_output_tokens": m.max_output_tokens,
            "cost_per_1k_input": m.cost_per_1k_input,
            "cost_per_1k_output": m.cost_per_1k_output,
            "speed_tier": m.speed_tier,
            "allowed": allowed,
            "is_gemma": "gemma" in m.name.lower(),
        })
    for m in LOCAL_MODELS:
        all_models.append({
            "name": m.name,
            "display_name": m.display_name,
            "provider": m.provider.value,
            "capabilities": m.capabilities,
            "reasoning_score": m.reasoning_score,
            "context_length": m.context_length,
            "max_output_tokens": m.max_output_tokens,
            "cost_per_1k_input": 0.0,
            "cost_per_1k_output": 0.0,
            "speed_tier": m.speed_tier,
            "allowed": True,
            "is_gemma": False,
        })
    return {"success": True, "data": all_models}


@router.get("/analytics/summary")
async def get_analytics_summary():
    return {"success": True, "data": analytics_store.get_summary()}


@router.get("/analytics/history")
async def get_analytics_history(limit: int = 50, search: Optional[str] = None):
    return {"success": True, "data": analytics_store.get_history(limit, search)}


@router.get("/analytics/models")
async def get_model_comparison():
    return {"success": True, "data": analytics_store.get_model_comparison()}


@router.delete("/analytics")
async def clear_analytics():
    analytics_store.clear()
    return {"success": True, "message": "Analytics cleared"}


@router.get("/task-types")
async def get_task_types():
    return {"success": True, "data": [t.value for t in TaskCategory]}


@router.get("/complexity-levels")
async def get_complexity_levels():
    return {"success": True, "data": [c.value for c in ComplexityLevel]}


@router.get("/config")
async def get_config():
    return {
        "success": True,
        "data": {
            "fireworks_base_url": settings.FIREWORKS_BASE_URL,
            "fireworks_api_key_set": bool(settings.FIREWORKS_API_KEY),
            "local_model_enabled": settings.LOCAL_MODEL_ENABLED,
            "local_model_name": settings.LOCAL_MODEL_NAME,
            "accuracy_threshold": settings.ACCURACY_THRESHOLD,
            "allowed_models": settings.ALLOWED_MODELS,
        },
    }


class SettingsUpdate(BaseModel):
    fireworks_base_url: Optional[str] = None
    fireworks_api_key: Optional[str] = None
    local_model_enabled: Optional[bool] = None
    local_model_name: Optional[str] = None
    allowed_models: Optional[str] = None


@router.post("/config")
async def update_config(request: SettingsUpdate):
    updates = {}
    if request.fireworks_base_url is not None:
        settings.FIREWORKS_BASE_URL = request.fireworks_base_url
        updates["fireworks_base_url"] = request.fireworks_base_url
    if request.fireworks_api_key is not None:
        settings.FIREWORKS_API_KEY = request.fireworks_api_key
        updates["fireworks_api_key"] = "***" if request.fireworks_api_key else "cleared"
    if request.local_model_enabled is not None:
        settings.LOCAL_MODEL_ENABLED = request.local_model_enabled
        updates["local_model_enabled"] = request.local_model_enabled
    if request.local_model_name is not None:
        settings.LOCAL_MODEL_NAME = request.local_model_name
        updates["local_model_name"] = request.local_model_name
    if request.allowed_models is not None:
        settings.ALLOWED_MODELS = [m.strip() for m in request.allowed_models.split(",") if m.strip()]
        updates["allowed_models"] = settings.ALLOWED_MODELS

    _save_env_file(settings)

    return {"success": True, "message": "Settings updated", "updated": updates}


def _save_env_file(s):
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    lines = [
        f"FIREWORKS_BASE_URL={s.FIREWORKS_BASE_URL}",
        f"FIREWORKS_API_KEY={s.FIREWORKS_API_KEY}",
        f"ALLOWED_MODELS={','.join(s.ALLOWED_MODELS)}",
        f"LOCAL_MODEL_ENABLED={'true' if s.LOCAL_MODEL_ENABLED else 'false'}",
        f"LOCAL_MODEL_NAME={s.LOCAL_MODEL_NAME}",
    ]
    with open(env_path, "w") as f:
        f.write("\n".join(lines) + "\n")
