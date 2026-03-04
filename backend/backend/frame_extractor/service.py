from __future__ import annotations

import subprocess
from pathlib import Path

from backend.settings import settings


def extract_frames(
    video_path: Path,
    out_dir: Path | None = None,
    percents: tuple[int, int, int] = (20, 50, 80),
) -> list[Path]:
    """Extract 3 representative frames using ffmpeg by seeking.

    This is fast and predictable; avoids heavy scene-detection.
    """
    video_path = video_path.expanduser().resolve()
    if not video_path.exists():
        raise FileNotFoundError(str(video_path))

    out_base = (out_dir or settings.frames_dir) / video_path.stem
    out_base.mkdir(parents=True, exist_ok=True)

    # Get duration (seconds) via ffprobe
    probe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    duration = float(probe.stdout.strip() or 0.0)
    if duration <= 0:
        raise RuntimeError(f"Could not probe duration for {video_path}")

    outputs: list[Path] = []
    for i, pct in enumerate(percents, start=1):
        ts = max(0.0, min(duration - 0.05, duration * (pct / 100.0)))
        out = out_base / f"frame_{i:02d}_{pct}.jpg"
        # -ss before -i is fast seeking
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-ss",
                f"{ts:.3f}",
                "-i",
                str(video_path),
                "-frames:v",
                "1",
                "-q:v",
                "2",
                str(out),
            ],
            capture_output=True,
            check=True,
        )
        outputs.append(out)

    return outputs
