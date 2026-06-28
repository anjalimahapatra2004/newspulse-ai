import os
# Works around a Windows DLL conflict: scikit-learn and PyTorch each bundle
# their own OpenMP runtime, and loading sklearn first can crash torch's
# load with a generic DLL init error. This is the standard, safe workaround.
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

from sentence_transformers import SentenceTransformer
import numpy as np

from app.exceptions import ExternalServiceError
from app.logger import get_logger

logger = get_logger(__name__)

# Loaded once at startup - keep this model warm in memory, not reloaded per request
try:
    _model = SentenceTransformer("all-MiniLM-L6-v2")
    logger.info("Sentence-Transformers model loaded: all-MiniLM-L6-v2")
except Exception:
    logger.error("Failed to load Sentence-Transformers model", exc_info=True)
    _model = None


def generate_embedding(text: str) -> list:
    """Returns a 384-dim embedding vector for the given text."""
    if _model is None:
        raise ExternalServiceError("The embedding model isn't available right now.")
    try:
        vector = _model.encode(text, normalize_embeddings=True)
        return vector.tolist()
    except Exception:
        logger.error("Embedding generation failed for text snippet", exc_info=True)
        raise ExternalServiceError("Couldn't generate an embedding for that article.")


def cosine_similarity(vec_a: list, vec_b: list) -> float:
    a, b = np.array(vec_a), np.array(vec_b)
    if a.size == 0 or b.size == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))