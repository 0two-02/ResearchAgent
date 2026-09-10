"""
ResearchPilot AI - Embeddings Service
Generates and manages text embeddings using sentence-transformers.
Falls back gracefully if the model isn't available.
"""
from typing import List, Optional
import numpy as np


_MODEL = None
_MODEL_NAME = None


def get_embedding_model(model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
    """Load embedding model lazily."""
    global _MODEL, _MODEL_NAME
    if _MODEL is None or _MODEL_NAME != model_name:
        try:
            from sentence_transformers import SentenceTransformer
            _MODEL = SentenceTransformer(model_name)
            _MODEL_NAME = model_name
            print(f"[Embeddings] Loaded model: {model_name}")
        except Exception as e:
            print(f"[Embeddings] Could not load sentence-transformers: {e}. Using random embeddings (demo mode).")
            _MODEL = None
    return _MODEL


def embed_texts(texts: List[str], model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> List[List[float]]:
    """
    Generate embeddings for a list of texts.
    Falls back to random vectors if the model is unavailable.
    """
    if not texts:
        return []
    model = get_embedding_model(model_name)
    if model is not None:
        try:
            embeddings = model.encode(texts, show_progress_bar=False, batch_size=32)
            return embeddings.tolist()
        except Exception as e:
            print(f"[Embeddings] Encoding error: {e}")
    # Fallback: random unit vectors (for demo/testing)
    dim = 384
    result = []
    for _ in texts:
        vec = np.random.randn(dim).astype(np.float32)
        vec /= np.linalg.norm(vec)
        result.append(vec.tolist())
    return result


def embed_single(text: str, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> List[float]:
    """Generate embedding for a single text."""
    results = embed_texts([text], model_name)
    return results[0] if results else []
