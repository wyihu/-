from __future__ import annotations

from pathlib import Path

from backend.model_provider.base import ModelProvider
from backend.types import ModelResult


class DeepSeekProvider(ModelProvider):
    name = "deepseek"

    def __init__(self, cfg: dict):
        self.api_key = cfg.get("api_key")
        self.model = cfg.get("model", "deepseek-chat")
        self.base_url = cfg.get("base_url", "https://api.deepseek.com")

    async def analyze_image(self, image_path: Path) -> ModelResult:
        # Placeholder: DeepSeek vision API specifics vary by offering.
        if not self.api_key or "${" in str(self.api_key):
            raise RuntimeError("DeepSeek api_key not configured. Set DEEPSEEK_API_KEY or edit config/models.yaml")
        _ = (image_path, self.model, self.base_url)
        return {"scene": "unknown", "action": "unknown", "object": "unknown"}
