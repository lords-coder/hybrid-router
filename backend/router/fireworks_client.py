import httpx
import time
import json
from config.settings import settings
from config.models import ModelInfo, ModelProvider, ALL_FIREWORKS_MODELS


_local_pipeline = None
_local_tokenizer = None


def _get_local_pipeline():
    global _local_pipeline, _local_tokenizer
    if _local_pipeline is not None:
        return _local_pipeline, _local_tokenizer

    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
        import torch

        model_name = settings.LOCAL_MODEL_NAME
        print(f"[LOCAL] Loading model: {model_name}")

        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            revision=settings.LOCAL_MODEL_REVISION or None,
            trust_remote_code=True,
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            revision=settings.LOCAL_MODEL_REVISION or None,
            torch_dtype=torch.float32,
            device_map="cpu",
            trust_remote_code=True,
        )

        _local_tokenizer = tokenizer
        _local_pipeline = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=512,
            do_sample=True,
            temperature=0.3,
        )
        print(f"[LOCAL] Model loaded successfully: {model_name}")
        return _local_pipeline, _local_tokenizer

    except Exception as e:
        print(f"[LOCAL] Failed to load model: {e}")
        return None, None


class LLMClient:
    def chat_completion(
        self,
        model: ModelInfo,
        prompt: str,
        system_prompt: str = "You are a helpful assistant.",
        temperature: float = 0.3,
        max_tokens: int = 512,
    ) -> dict:
        if model.provider == ModelProvider.LOCAL:
            return self._call_local(model, prompt, system_prompt, temperature, max_tokens)
        else:
            return self._call_fireworks(model, prompt, system_prompt, temperature, max_tokens)

    def _call_local(
        self, model: ModelInfo, prompt: str, system_prompt: str,
        temperature: float, max_tokens: int,
    ) -> dict:
        pipe, tokenizer = _get_local_pipeline()
        if pipe is None:
            return {
                "success": False,
                "error": "Local model not available. Falling back to Fireworks.",
                "model": model.name,
                "model_display": model.display_name,
                "provider": "local",
                "processing_time_ms": 0,
            }

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        start = time.time()
        try:
            text = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            outputs = pipe(text, max_new_tokens=max_tokens, temperature=temperature)
            generated = outputs[0]["generated_text"]
            content = generated[len(text):].strip()

            elapsed = (time.time() - start) * 1000

            input_tokens = len(tokenizer.encode(text))
            output_tokens = len(tokenizer.encode(content))

            return {
                "success": True,
                "content": content,
                "model": model.name,
                "model_display": model.display_name,
                "provider": "local",
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "fireworks_tokens": 0,
                "processing_time_ms": round(elapsed, 2),
            }
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return {
                "success": False,
                "error": f"Local model error: {str(e)[:200]}",
                "model": model.name,
                "model_display": model.display_name,
                "provider": "local",
                "processing_time_ms": round(elapsed, 2),
            }

    def _call_fireworks(
        self, model: ModelInfo, prompt: str, system_prompt: str,
        temperature: float, max_tokens: int,
    ) -> dict:
        if not settings.FIREWORKS_API_KEY:
            return {
                "success": False,
                "error": "FIREWORKS_API_KEY not set. Cannot call Fireworks API.",
                "model": model.name,
                "model_display": model.display_name,
                "provider": "fireworks",
                "processing_time_ms": 0,
            }

        base_url = settings.FIREWORKS_BASE_URL.rstrip("/")
        url = f"{base_url}/chat/completions"

        payload = {
            "model": model.name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": min(max_tokens, model.max_output_tokens),
        }

        headers = {
            "Authorization": f"Bearer {settings.FIREWORKS_API_KEY}",
            "Content-Type": "application/json",
        }

        start = time.time()
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(url, json=payload, headers=headers)

            elapsed = (time.time() - start) * 1000

            if response.status_code != 200:
                error_detail = ""
                try:
                    err_data = response.json()
                    error_detail = err_data.get("error", {}).get("message", "") or str(err_data)[:200]
                except Exception:
                    error_detail = response.text[:200]

                return {
                    "success": False,
                    "error": f"Fireworks API {response.status_code}: {error_detail}",
                    "model": model.name,
                    "model_display": model.display_name,
                    "provider": "fireworks",
                    "processing_time_ms": round(elapsed, 2),
                }

            data = response.json()

            content = ""
            if "choices" in data and len(data["choices"]) > 0:
                choice = data["choices"][0]
                if "message" in choice:
                    content = choice["message"].get("content", "")

            usage = data.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)

            return {
                "success": True,
                "content": content,
                "model": model.name,
                "model_display": model.display_name,
                "provider": "fireworks",
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "fireworks_tokens": input_tokens + output_tokens,
                "processing_time_ms": round(elapsed, 2),
            }

        except httpx.ConnectError:
            elapsed = (time.time() - start) * 1000
            return {
                "success": False,
                "error": f"Cannot connect to Fireworks API at {url}. Check your network and FIREWORKS_BASE_URL.",
                "model": model.name,
                "model_display": model.display_name,
                "provider": "fireworks",
                "processing_time_ms": round(elapsed, 2),
            }
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return {
                "success": False,
                "error": f"Fireworks API error: {str(e)[:300]}",
                "model": model.name,
                "model_display": model.display_name,
                "provider": "fireworks",
                "processing_time_ms": round(elapsed, 2),
            }

    def try_fallback(
        self, failed_model: ModelInfo, prompt: str, system_prompt: str,
        temperature: float, max_tokens: int,
    ) -> dict:
        if settings.LOCAL_MODEL_ENABLED:
            local_models = [m for m in ALL_FIREWORKS_MODELS if m.provider == ModelProvider.LOCAL]
            for lm in local_models:
                result = self._call_local(lm, prompt, system_prompt, temperature, max_tokens)
                if result["success"]:
                    result["note"] = f"Fallback: {lm.display_name}"
                    return result

        allowed = [m for m in ALL_FIREWORKS_MODELS if m.provider == ModelProvider.FIREWORKS]
        if settings.ALLOWED_MODELS:
            allowed = [m for m in allowed if m.name in settings.ALLOWED_MODELS]

        for m in allowed:
            if m.name == failed_model.name:
                continue
            if settings.FIREWORKS_API_KEY:
                result = self._call_fireworks(m, prompt, system_prompt, temperature, max_tokens)
                if result["success"]:
                    result["note"] = f"Fallback: {failed_model.display_name} -> {m.display_name}"
                    return result

        error_msg = "All models failed. "
        if not settings.FIREWORKS_API_KEY:
            error_msg += "FIREWORKS_API_KEY is not set. Go to Settings to add your key."
        else:
            error_msg += "Your Fireworks API key may be invalid. Go to Settings to update it."
        return {
            "success": False,
            "error": error_msg,
            "model": failed_model.name,
            "model_display": failed_model.display_name,
            "provider": failed_model.provider.value,
            "processing_time_ms": 0,
        }


llm_client = LLMClient()
