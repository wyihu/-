from __future__ import annotations

import base64
from pathlib import Path

import httpx

from backend.model_provider.base import ModelProvider
from backend.types import ModelResult


class OpenAIProvider(ModelProvider):
    name = "openai"

    def __init__(self, cfg: dict):
        self.api_key = cfg.get("api_key")
        self.model = cfg.get("model", "gpt-4o-mini")
        self.base_url = cfg.get("base_url", "https://api.openai.com/v1")

    async def analyze_image(self, image_path: Path) -> ModelResult:
        if not self.api_key or "${" in str(self.api_key):
            raise RuntimeError("OpenAI api_key not configured. Set OPENAI_API_KEY or edit config/models.yaml")

        img_b64 = base64.b64encode(image_path.read_bytes()).decode("utf-8")
        prompt = (
            "You are a vision tagger. Return STRICT JSON with keys: scene, action, object. "
            "Use short lowercase tokens."
        )
        payload = {
            "model": self.model,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"},
                        },
                    ],
                }
            ],
        }

        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
            )
            r.raise_for_status()
            data = r.json()

        content = data["choices"][0]["message"]["content"]
        # content should already be JSON
        import json

        obj = json.loads(content)
        return {
            "scene": str(obj.get("scene", "unknown")),
            "action": str(obj.get("action", "unknown")),
            "object": str(obj.get("object", "unknown")),
        }
