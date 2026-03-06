from __future__ import annotations

from typing import Any

import httpx

from backend.core.config import COMFYUI_BASE_URL
from backend.providers.base.provider_base import ProviderBase


class ComfyUIProvider(ProviderBase):
    provider_name = "comfyui"

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or COMFYUI_BASE_URL).rstrip("/")

    def health_check(self) -> dict[str, Any]:
        try:
            response = httpx.get(f"{self.base_url}/system_stats", timeout=5)
            response.raise_for_status()
            return {"provider": self.provider_name, "status": "ok", "base_url": self.base_url}
        except Exception as exc:  # noqa: BLE001
            return {
                "provider": self.provider_name,
                "status": "error",
                "base_url": self.base_url,
                "error": str(exc),
            }

    def list_capabilities(self) -> list[str]:
        return ["text_to_image", "image_to_image", "workflow_prompt_submit"]

    def list_models(self) -> list[dict[str, Any]]:
        try:
            object_info_response = httpx.get(f"{self.base_url}/object_info", timeout=8)
            object_info_response.raise_for_status()
            object_info = object_info_response.json()

            ckpt_values = (
                object_info.get("CheckpointLoaderSimple", {})
                .get("input", {})
                .get("required", {})
                .get("ckpt_name", [[]])[0]
            )
            if isinstance(ckpt_values, list) and ckpt_values:
                return [
                    {"model_key": model_name, "display_name": model_name, "source": "object_info"}
                    for model_name in ckpt_values
                ]
        except Exception:  # noqa: BLE001
            pass

        try:
            fallback_response = httpx.get(f"{self.base_url}/models", timeout=8)
            fallback_response.raise_for_status()
            data = fallback_response.json()
            if isinstance(data, list):
                return [{"model_key": str(item), "display_name": str(item), "source": "models"} for item in data]
        except Exception:  # noqa: BLE001
            pass

        return []

    def submit_job(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = httpx.post(f"{self.base_url}/prompt", json=payload, timeout=20)
        response.raise_for_status()
        body = response.json()
        return {
            "provider": self.provider_name,
            "provider_job_id": body.get("prompt_id") or body.get("id"),
            "raw_response": body,
            "status": "PENDING",
        }

    def get_job_status(self, job_id: str) -> dict[str, Any]:
        try:
            history_response = httpx.get(f"{self.base_url}/history/{job_id}", timeout=8)
            history_response.raise_for_status()
            history_body = history_response.json()
            if isinstance(history_body, dict) and job_id in history_body:
                return {"provider_job_id": job_id, "status": "SUCCEEDED", "raw": history_body[job_id]}
        except Exception:  # noqa: BLE001
            pass

        try:
            queue_response = httpx.get(f"{self.base_url}/queue", timeout=8)
            queue_response.raise_for_status()
            queue_body = queue_response.json()
            running = queue_body.get("queue_running", []) if isinstance(queue_body, dict) else []
            pending = queue_body.get("queue_pending", []) if isinstance(queue_body, dict) else []

            if any(job_id in str(item) for item in running):
                return {"provider_job_id": job_id, "status": "RUNNING", "raw": queue_body}
            if any(job_id in str(item) for item in pending):
                return {"provider_job_id": job_id, "status": "PENDING", "raw": queue_body}
        except Exception:  # noqa: BLE001
            pass

        return {"provider_job_id": job_id, "status": "UNKNOWN", "raw": {}}

    def cancel_job(self, job_id: str) -> dict[str, Any]:
        return {"provider_job_id": job_id, "status": "NOT_IMPLEMENTED", "note": "TODO: call ComfyUI queue delete API"}

    def fetch_outputs(self, job_id: str) -> dict[str, Any]:
        response = httpx.get(f"{self.base_url}/history/{job_id}", timeout=8)
        response.raise_for_status()
        history_body = response.json()
        job_data = history_body.get(job_id, {}) if isinstance(history_body, dict) else {}
        outputs = job_data.get("outputs", {}) if isinstance(job_data, dict) else {}
        return {"provider_job_id": job_id, "outputs": outputs}
