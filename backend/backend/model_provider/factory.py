from __future__ import annotations

from backend.model_provider.base import ModelProvider
from backend.model_provider.local_provider import LocalProvider
from backend.model_provider.openai_provider import OpenAIProvider
from backend.model_provider.google_provider import GoogleProvider
from backend.model_provider.deepseek_provider import DeepSeekProvider
from backend.model_provider.qwen_provider import QwenProvider
from backend.types import ProviderKind


def create_provider(kind: ProviderKind, cfg: dict) -> ModelProvider:
    if kind == "local":
        return LocalProvider(cfg)
    if kind == "openai":
        return OpenAIProvider(cfg)
    if kind == "google":
        return GoogleProvider(cfg)
    if kind == "deepseek":
        return DeepSeekProvider(cfg)
    if kind == "qwen":
        return QwenProvider(cfg)
    raise ValueError(f"Unknown provider kind: {kind}")
