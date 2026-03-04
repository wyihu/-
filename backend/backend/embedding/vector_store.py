from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import faiss
import numpy as np


@dataclass
class VectorStorePaths:
    root: Path

    @property
    def index_path(self) -> Path:
        return self.root / "vectors.index"

    @property
    def meta_path(self) -> Path:
        return self.root / "metadata.json"


class VectorStore:
    """Simple FAISS-backed vector store.

    - Cosine similarity is handled by storing normalized embeddings
      and using inner product (IndexFlatIP).
    """

    def __init__(self, root: Path, dim: int = 512):
        self.paths = VectorStorePaths(root=root)
        self.dim = dim
        self.paths.root.mkdir(parents=True, exist_ok=True)

        self.index = faiss.IndexFlatIP(dim)
        self.metadata: list[dict[str, Any]] = []

        if self.paths.index_path.exists() and self.paths.meta_path.exists():
            self._load()

    def _load(self) -> None:
        self.index = faiss.read_index(str(self.paths.index_path))
        self.metadata = json.loads(self.paths.meta_path.read_text(encoding="utf-8"))

    def save(self) -> None:
        faiss.write_index(self.index, str(self.paths.index_path))
        self.paths.meta_path.write_text(
            json.dumps(self.metadata, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def reset(self) -> None:
        self.index = faiss.IndexFlatIP(self.dim)
        self.metadata = []
        # do not delete files automatically

    def add(self, vector: np.ndarray, meta: dict[str, Any]) -> None:
        v = np.asarray(vector, dtype="float32").reshape(1, -1)
        if v.shape[1] != self.dim:
            raise ValueError(f"dim mismatch: got {v.shape[1]} expected {self.dim}")
        self.index.add(v)
        self.metadata.append(meta)

    def search(self, vector: np.ndarray, top_k: int = 5) -> list[dict[str, Any]]:
        if self.index.ntotal == 0:
            return []
        v = np.asarray(vector, dtype="float32").reshape(1, -1)
        scores, idxs = self.index.search(v, top_k)
        out: list[dict[str, Any]] = []
        for score, idx in zip(scores[0].tolist(), idxs[0].tolist()):
            if idx < 0 or idx >= len(self.metadata):
                continue
            out.append({"score": float(score), **self.metadata[idx]})
        return out
