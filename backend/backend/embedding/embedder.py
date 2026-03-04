from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "openai/clip-vit-base-patch32"  # 512-d


@lru_cache(maxsize=1)
def _model() -> SentenceTransformer:
    # SentenceTransformer supports CLIP model + image/text encoders.
    return SentenceTransformer(MODEL_NAME)


def encode_image(image_path: Path) -> np.ndarray:
    """Encode an image into a 512-d float32 vector."""
    image_path = Path(image_path).expanduser().resolve()
    if not image_path.exists():
        raise FileNotFoundError(str(image_path))

    model = _model()
    emb = model.encode(
        [str(image_path)],
        batch_size=1,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    v = emb[0].astype("float32")
    if v.shape[0] != 512:
        raise RuntimeError(f"Unexpected embedding dim {v.shape[0]} (expected 512)")
    return v


def encode_text(text: str) -> np.ndarray:
    """Encode a query string into a 512-d float32 vector."""
    model = _model()
    emb = model.encode(
        [text],
        batch_size=1,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    v = emb[0].astype("float32")
    if v.shape[0] != 512:
        raise RuntimeError(f"Unexpected embedding dim {v.shape[0]} (expected 512)")
    return v
