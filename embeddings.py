"""
Shared embedding model loader. Every module that needs the sentence-transformer
embedding model should import _get_embedding_model from here instead of keeping
its own copy — otherwise each importer loads the model from disk independently,
which is pure wasted time (this was costing ~15s per module on first call).
"""

from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

_embedding_model = None


def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedding_model
