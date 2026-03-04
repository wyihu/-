from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from backend.settings import settings
from backend.types import VideoItem


def scan_videos(clips_dir: Path | None = None) -> list[VideoItem]:
    base = clips_dir or settings.clips_dir
    base = base.expanduser().resolve()
    if not base.exists():
        return []

    videos = sorted(base.rglob("*.mp4"))
    return [VideoItem(path=p, name=p.name) for p in videos]


def scan_videos_dict(clips_dir: Path | None = None) -> list[dict]:
    return [asdict(v) | {"path": str(v.path)} for v in scan_videos(clips_dir)]
