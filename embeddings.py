"""
Shared embedding model loader. Every module that needs the sentence-transformer
embedding model should import get_embedding_model from here instead of keeping
its own copy — otherwise each importer loads the model from disk independently,
which is pure wasted time.

# First-time setup/download (must be run once with internet access):
# python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-m3', max_seq_length=512)"
"""

from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL_NAME = "BAAI/bge-m3"

_embedding_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        # Load the model with max_seq_length=512
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME, max_seq_length=512)
    return _embedding_model
