from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from backend.types import ModelResult


class ModelProvider(ABC):
    name: str

    @abstractmethod
    async def analyze_image(self, image_path: Path) -> ModelResult:
        """Return structured tags from a single frame."""
        raise NotImplementedError
