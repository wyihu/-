from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.types import Tag


def load_index(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def upsert_item(path: Path, file: str, tag: Tag) -> dict[str, Any]:
    items = load_index(path)
    items = [i for i in items if i.get("file") != file]
    item = {
        "file": file,
        "scene": tag.scene,
        "action": tag.action,
        "object": tag.object,
        "shot": tag.shot,
    }
    items.append(item)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    return item
