from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.embedding.embedder import encode_image
from backend.embedding.vector_store import VectorStore
from backend.frame_extractor.service import extract_frames


def build_index(
    items: list[dict[str, Any]],
    store_root: Path = Path("storage") / "embeddings",
    library_dir: Path = Path("storage") / "library",
) -> dict[str, Any]:
    """Rebuild embeddings store from a list of library items.

    For each video file, extract a representative frame and embed it.
    """

    store = VectorStore(store_root)
    store.reset()

    ok = 0
    failed: list[dict[str, Any]] = []

    for it in items:
        file = it.get("file")
        if not file:
            continue
        video_path = (library_dir / file).resolve()
        try:
            frames = extract_frames(video_path)
            frame = frames[1] if len(frames) >= 2 else frames[0]
            vec = encode_image(frame)
            meta = {k: it.get(k) for k in ["file", "scene", "action", "object", "shot"]}
            store.add(vec, meta)
            ok += 1
        except Exception as e:
            failed.append({"file": file, "error": str(e)})

    store.save()
    return {"count": ok, "failed": failed, "index": str(store.paths.index_path)}
