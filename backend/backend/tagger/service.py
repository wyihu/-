from __future__ import annotations

from backend.types import ModelResult, Tag


def to_tag(model_result: ModelResult) -> Tag:
    # Normalize + ensure keys exist
    scene = (model_result.get("scene") or "unknown").strip().lower()
    action = (model_result.get("action") or "unknown").strip().lower()
    obj = (model_result.get("object") or "unknown").strip().lower()
    return Tag(scene=scene, action=action, object=obj, shot=None)
