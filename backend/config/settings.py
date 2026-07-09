import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    FIREWORKS_BASE_URL: str = os.getenv("FIREWORKS_BASE_URL", "https://api.fireworks.ai/inference/v1")
    FIREWORKS_API_KEY: str = os.getenv("FIREWORKS_API_KEY", "")
    ALLOWED_MODELS: list[str] = [
        m.strip() for m in os.getenv("ALLOWED_MODELS", "").split(",") if m.strip()
    ]

    LOCAL_MODEL_ENABLED: bool = os.getenv("LOCAL_MODEL_ENABLED", "false").lower() == "true"
    LOCAL_MODEL_NAME: str = os.getenv("LOCAL_MODEL_NAME", "Qwen/Qwen2.5-0.5B-Instruct")
    LOCAL_MODEL_REVISION: str = os.getenv("LOCAL_MODEL_REVISION", "")

    DEFAULT_TEMPERATURE: float = 0.3
    DEFAULT_MAX_TOKENS: int = 512
    ACCURACY_THRESHOLD: float = 0.65

    INPUT_DIR: str = os.getenv("INPUT_DIR", "/input")
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "/output")

    def update(self, **kwargs):
        for key, value in kwargs.items():
            key_upper = key.upper()
            if hasattr(self, key_upper):
                current = getattr(self, key_upper)
                if isinstance(current, bool):
                    setattr(self, key_upper, str(value).lower() == "true")
                elif isinstance(current, list):
                    setattr(self, key_upper, [m.strip() for m in str(value).split(",") if m.strip()])
                else:
                    setattr(self, key_upper, type(current)(value))


settings = Settings()


def check_torch_available() -> bool:
    try:
        import torch
        return True
    except ImportError:
        return False


TORCH_AVAILABLE = check_torch_available()

if settings.LOCAL_MODEL_ENABLED and not TORCH_AVAILABLE:
    print("[SETTINGS] WARNING: LOCAL_MODEL_ENABLED=true but torch is not installed. Disabling local model.")
    settings.LOCAL_MODEL_ENABLED = False
