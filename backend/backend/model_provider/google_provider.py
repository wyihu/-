from __future__ import annotations

from pathlib import Path

from backend.model_provider.base import ModelProvider
from backend.types import ModelResult


class GoogleProvider(ModelProvider):
    name = "google"

    def __init__(self, cfg: dict):
        self.api_key = cfg.get("api_key")
        self.model = cfg.get("model", "gemini-1.5-flash")

    async def analyze_image(self, image_path: Path) -> ModelResult:
        # Intentionally lightweight placeholder to keep the project runnable without extra deps.
        # You can implement using google-genai / Vertex later.
        if not self.api_key or "${" in str(self.api_key):
            raise RuntimeError("Google api_key not configured. Set GOOGLE_API_KEY or edit config/models.yaml")
        _ = (image_path, self.model)
        return {"scene": "unknown", "action": "unknown", "object": "unknown"}
