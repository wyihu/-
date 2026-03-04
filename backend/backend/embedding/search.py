from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.embedding.embedder import encode_text
from backend.embedding.vector_store import VectorStore


def search_videos(query: str, top_k: int = 5, store_root: Path = Path("storage") / "embeddings") -> list[dict[str, Any]]:
    """Text -> CLIP text embedding -> FAISS similarity search."""
    store = VectorStore(store_root)
    q = encode_text(query)
    hits = store.search(q, top_k=top_k)
    # shape to API format
    return [{"file": h.get("file"), "score": round(float(h.get("score", 0.0)), 4)} for h in hits]
