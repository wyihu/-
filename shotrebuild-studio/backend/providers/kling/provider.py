from backend.providers.base.provider_base import ProviderBase


class KlingProvider(ProviderBase):
    provider_name = "kling"

    def health_check(self) -> dict:
        return {"provider": self.provider_name, "status": "mock-ok", "note": "TODO: connect real Kling automation"}

    def list_capabilities(self) -> list[str]:
        return ["text_to_video", "image_to_video", "extend_video"]

    def list_models(self) -> list[dict]:
        return [{"model_key": "kling/mock-1.6", "display_name": "Kling Mock 1.6"}]

    def submit_job(self, payload: dict) -> dict:
        return {"job_id": "kling-job-mock-001", "status": "queued", "payload": payload}

    def get_job_status(self, job_id: str) -> dict:
        return {"job_id": job_id, "status": "running", "progress": 0.65}

    def cancel_job(self, job_id: str) -> dict:
        return {"job_id": job_id, "status": "cancelled"}

    def fetch_outputs(self, job_id: str) -> dict:
        return {"job_id": job_id, "outputs": [], "note": "TODO: fetch real Kling outputs"}
