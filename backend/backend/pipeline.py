from __future__ import annotations

import asyncio
from dataclasses import asdict
from pathlib import Path
from typing import Any

from backend.frame_extractor.service import extract_frames
from backend.indexer.service import upsert_item
from backend.model_provider.config import load_models_config
from backend.model_provider.factory import create_provider
from backend.renamer.service import rename_video
from backend.settings import settings
from backend.tagger.service import to_tag
from backend.embedding.embedder import encode_image
from backend.embedding.vector_store import VectorStore


async def analyze_video(video_path: Path) -> dict[str, Any]:
    cfg = load_models_config(settings.models_config_path)
    provider_cfg = cfg.providers.get(cfg.active_provider, {})
    provider = create_provider(cfg.active_provider, provider_cfg)

    frames = extract_frames(video_path)
    # Analyze 3 frames concurrently
    results = await asyncio.gather(*(provider.analyze_image(p) for p in frames))

    # simple merge heuristic: take the first non-unknown token per field
    def pick(key: str) -> str:
        for r in results:
            v = (r.get(key) or "").strip().lower()
            if v and v != "unknown":
                return v
        return "unknown"

    tag = to_tag({"scene": pick("scene"), "action": pick("action"), "object": pick("object")})

    # rename into storage/library
    library_dir = settings.index_path.parent
    renamed = rename_video(video_path, dest_dir=library_dir, action=tag.action)

    item = upsert_item(settings.index_path, file=renamed.name, tag=tag)

    # Embedding: use the middle frame by default, store into FAISS.
    try:
        frame_for_embed = frames[1] if len(frames) >= 2 else frames[0]
        vec = encode_image(frame_for_embed)
        store = VectorStore(Path("storage") / "embeddings")
        store.add(vec, {"file": renamed.name, "scene": tag.scene, "action": tag.action, "object": tag.object})
        store.save()
    except Exception:
        # Embeddings are optional; pipeline must remain usable.
        pass

    return {
        "video": str(video_path),
        "renamed_to": str(renamed),
        "tag": asdict(tag),
        "index_item": item,
        "provider": cfg.active_provider,
        "frames": [str(p) for p in frames],
    }
