from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional, TypedDict


class ModelResult(TypedDict):
    scene: str
    action: str
    object: str


@dataclass
class VideoItem:
    path: Path
    name: str


@dataclass
class Tag:
    scene: str
    action: str
    object: str
    shot: Optional[str] = None


ProviderKind = Literal["local", "openai", "google", "deepseek", "qwen"]
