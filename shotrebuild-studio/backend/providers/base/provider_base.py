from abc import ABC, abstractmethod
from typing import Any


class ProviderBase(ABC):
    """Provider placeholder abstraction for future real integrations."""

    provider_name: str

    @abstractmethod
    def health_check(self) -> dict[str, Any]:
        pass

    @abstractmethod
    def list_capabilities(self) -> list[str]:
        pass

    @abstractmethod
    def list_models(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def submit_job(self, payload: dict[str, Any]) -> dict[str, Any]:
        pass

    @abstractmethod
    def get_job_status(self, job_id: str) -> dict[str, Any]:
        pass

    @abstractmethod
    def cancel_job(self, job_id: str) -> dict[str, Any]:
        pass

    @abstractmethod
    def fetch_outputs(self, job_id: str) -> dict[str, Any]:
        pass
