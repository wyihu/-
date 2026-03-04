from __future__ import annotations

from typing import Any, Literal

import httpx


OllamaStatus = Literal["running", "offline"]


def check_ollama(
    host: str = "http://localhost:11434",
    required_model: str = "llava:13b",
) -> dict[str, Any]:
    """Check Ollama service + required model availability.

    Calls GET {host}/api/tags.

    Returns one of:
      - {"provider":"ollama","status":"offline"}
      - {"provider":"ollama","status":"running","models":[...]}
      - {"provider":"ollama","status":"running","model":"missing","models":[...]}
    """

    base = host.rstrip("/")
    url = f"{base}/api/tags"

    try:
        r = httpx.get(url, timeout=3.0)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return {"provider": "ollama", "status": "offline"}

    models_raw = data.get("models") or []
    models: list[str] = []
    for m in models_raw:
        if isinstance(m, dict) and m.get("name"):
            models.append(str(m["name"]))
        elif isinstance(m, str):
            models.append(m)

    result: dict[str, Any] = {"provider": "ollama", "status": "running", "models": models}
    if required_model and required_model not in models:
        result["model"] = "missing"
    return result
