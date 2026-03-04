from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

import httpx

from backend.model_provider.base import ModelProvider
from backend.types import ModelResult


class LocalProvider(ModelProvider):
    """Local vision provider backed by Ollama + LLaVA.

    Uses Ollama Generate API:
      POST {host}/api/generate
    Payload:
      {"model": "llava:13b", "prompt": "...", "images": ["<base64>"], "stream": false}
    """

    name = "local"

    def __init__(self, cfg: dict | None = None):
        cfg = cfg or {}
        self.provider = cfg.get("provider", "ollama")
        self.model = cfg.get("model", "llava:13b")
        self.host = (cfg.get("host") or "http://localhost:11434").rstrip("/")

    async def analyze_image(self, image_path: Path) -> ModelResult:
        image_path = image_path.expanduser().resolve()
        if not image_path.exists():
            raise FileNotFoundError(str(image_path))

        if self.provider != "ollama":
            # keep strict: only ollama for now
            return {"scene": "unknown", "action": "unknown", "object": "unknown"}

        prompt = (
            'Analyze the image and output JSON: { "scene":"", "action":"", "object":"" } '
            "Return only JSON."
        )

        img_b64 = base64.b64encode(image_path.read_bytes()).decode("utf-8")
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "images": [img_b64],
            "stream": False,
        }

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                r = await client.post(f"{self.host}/api/generate", json=payload)
                r.raise_for_status()
                data = r.json()
        except Exception:
            return {"scene": "unknown", "action": "unknown", "object": "unknown"}

        # Ollama returns {response: "...", done: true, ...}
        text = (data.get("response") or "").strip()
        if not text:
            return {"scene": "unknown", "action": "unknown", "object": "unknown"}

        # Try parse strict JSON; if model leaked extra text, attempt to extract the JSON object.
        obj: dict[str, Any] | None = None
        try:
            obj = json.loads(text)
        except Exception:
            # naive extraction of first {...}
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    obj = json.loads(text[start : end + 1])
                except Exception:
                    obj = None

        if not isinstance(obj, dict):
            return {"scene": "unknown", "action": "unknown", "object": "unknown"}

        scene = str(obj.get("scene", "unknown") or "unknown").strip().lower()
        action = str(obj.get("action", "unknown") or "unknown").strip().lower()
        object_ = str(obj.get("object", "unknown") or "unknown").strip().lower()

        if not scene:
            scene = "unknown"
        if not action:
            action = "unknown"
        if not object_:
            object_ = "unknown"

        return {"scene": scene, "action": action, "object": object_}
