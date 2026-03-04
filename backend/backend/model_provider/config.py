from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from backend.types import ProviderKind


@dataclass
class ModelsConfig:
    active_provider: ProviderKind
    providers: dict[str, dict[str, Any]]


def _expand_env(value: Any) -> Any:
    if isinstance(value, str):
        return os.path.expandvars(value)
    if isinstance(value, dict):
        return {k: _expand_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand_env(v) for v in value]
    return value


def load_models_config(path: Path) -> ModelsConfig:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    raw = _expand_env(raw)
    active = raw.get("active_provider", "local")
    providers = raw.get("providers", {})
    return ModelsConfig(active_provider=active, providers=providers)


def save_models_config(path: Path, cfg: ModelsConfig) -> None:
    payload = {
        "active_provider": cfg.active_provider,
        "providers": cfg.providers,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
