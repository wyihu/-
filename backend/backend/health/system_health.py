from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from backend.settings import settings


def check_ffmpeg() -> dict[str, Any]:
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True, text=True)
        return {"status": "ok"}
    except Exception as e:
        return {"status": "missing", "error": str(e)}


def check_clips_dir() -> dict[str, Any]:
    clips = settings.clips_dir.expanduser()
    if clips.exists() and clips.is_dir():
        return {"status": "ok", "path": str(clips)}
    return {"status": "missing", "path": str(clips)}


def check_storage_writable() -> dict[str, Any]:
    lib_dir = settings.index_path.parent
    try:
        lib_dir.mkdir(parents=True, exist_ok=True)
        probe = lib_dir / ".write_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return {"status": "ok", "path": str(lib_dir)}
    except Exception as e:
        return {"status": "readonly", "path": str(lib_dir), "error": str(e)}


def system_health() -> dict[str, Any]:
    ff = check_ffmpeg()
    clips = check_clips_dir()
    storage = check_storage_writable()

    # ok only if all ok
    ok = ff.get("status") == "ok" and clips.get("status") == "ok" and storage.get("status") == "ok"
    return {
        "system": "ok" if ok else "degraded",
        "ffmpeg": ff.get("status"),
        "clips": clips.get("status"),
        "storage": storage.get("status"),
        "details": {"ffmpeg": ff, "clips": clips, "storage": storage},
    }
