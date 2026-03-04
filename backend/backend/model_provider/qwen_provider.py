from __future__ import annotations

from pathlib import Path

from backend.model_provider.base import ModelProvider
from backend.types import ModelResult


class QwenProvider(ModelProvider):
    name = "qwen"

    def __init__(self, cfg: dict):
        self.api_key = cfg.get("api_key")
        self.model = cfg.get("model", "qwen2.5-vl")
        self.base_url = cfg.get("base_url", "https://dashscope.aliyuncs.com")

    async def analyze_image(self, image_path: Path) -> ModelResult:
        # Placeholder: implement with DashScope/Qwen-VL API.
        if not self.api_key or "${" in str(self.api_key):
            raise RuntimeError("Qwen api_key not configured. Set QWEN_API_KEY or edit config/models.yaml")
        _ = (image_path, self.model, self.base_url)
        return {"scene": "unknown", "action": "unknown", "object": "unknown"}
