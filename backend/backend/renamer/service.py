from __future__ import annotations

from pathlib import Path


def next_name(action: str, index_dir: Path, ext: str = ".mp4") -> str:
    index_dir.mkdir(parents=True, exist_ok=True)
    existing = sorted(index_dir.glob(f"{action}_*.{ext.lstrip('.')}"))
    if not existing:
        return f"{action}_001{ext}"

    last = existing[-1].stem  # action_001
    try:
        n = int(last.split("_")[-1]) + 1
    except Exception:
        n = len(existing) + 1
    return f"{action}_{n:03d}{ext}"


def rename_video(src: Path, dest_dir: Path, action: str) -> Path:
    src = src.resolve()
    dest_dir = dest_dir.resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)
    new_name = next_name(action=action, index_dir=dest_dir, ext=src.suffix)
    dest = dest_dir / new_name
    src.rename(dest)
    return dest
