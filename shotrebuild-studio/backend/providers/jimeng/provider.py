from backend.providers.base.provider_base import ProviderBase


class JimengProvider(ProviderBase):
    provider_name = "jimeng"

    def health_check(self) -> dict:
        return {"provider": self.provider_name, "status": "mock-ok", "note": "TODO: connect real Jimeng automation"}

    def list_capabilities(self) -> list[str]:
        return ["text_to_video", "image_to_video"]

    def list_models(self) -> list[dict]:
        return [{"model_key": "jimeng/mock-v1", "display_name": "Jimeng Mock V1"}]

    def submit_job(self, payload: dict) -> dict:
        return {"job_id": "jimeng-job-mock-001", "status": "queued", "payload": payload}

    def get_job_status(self, job_id: str) -> dict:
        return {"job_id": job_id, "status": "running", "progress": 0.3}

    def cancel_job(self, job_id: str) -> dict:
        return {"job_id": job_id, "status": "cancelled"}

    def fetch_outputs(self, job_id: str) -> dict:
        return {"job_id": job_id, "outputs": [], "note": "TODO: fetch real Jimeng outputs"}
