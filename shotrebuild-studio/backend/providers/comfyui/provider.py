from backend.providers.base.provider_base import ProviderBase


class ComfyUIProvider(ProviderBase):
    provider_name = "comfyui"

    def health_check(self) -> dict:
        return {"provider": self.provider_name, "status": "mock-ok", "note": "TODO: connect real ComfyUI API"}

    def list_capabilities(self) -> list[str]:
        return ["text_to_image", "image_to_image"]

    def list_models(self) -> list[dict]:
        return [{"model_key": "comfyui/mock-sd", "display_name": "ComfyUI Mock SD"}]

    def submit_job(self, payload: dict) -> dict:
        return {"job_id": "comfyui-job-mock-001", "status": "queued", "payload": payload}

    def get_job_status(self, job_id: str) -> dict:
        return {"job_id": job_id, "status": "running", "progress": 0.42}

    def cancel_job(self, job_id: str) -> dict:
        return {"job_id": job_id, "status": "cancelled"}

    def fetch_outputs(self, job_id: str) -> dict:
        return {"job_id": job_id, "outputs": [], "note": "TODO: fetch real ComfyUI outputs"}
