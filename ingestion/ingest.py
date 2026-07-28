"""
Ingestion entry point: turns one case PDF into embedded chunks + an embedded
case-level summary, both stored in ChromaDB.

Assumes the caller has already checked check_if_exists(case_name) and decided
this case is new — this function does not check for duplicates itself, and
will happily create duplicate records if called twice on the same case.
"""

import os

import chromadb
from sentence_transformers import SentenceTransformer

from parser import chunk_pdf
from summarizer import summarize_case

CHROMA_PATH = "data/chroma_db"
CHUNKS_COLLECTION = "legal_chunks"
CASES_COLLECTION = "legal_cases"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Loaded once per process rather than per call — re-loading the model on
# every ingest_new_case() call would be needlessly slow for multi-PDF runs.
_embedding_model = None


def _get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedding_model


def ingest_new_case(filepath):
    """
    Ingest one case PDF: chunk it, embed + store each chunk, then generate
    and embed + store a case-level summary.

    Args:
        filepath: path to the case PDF.

    Returns:
        str: the case_name that was ingested (PDF filename without
        extension), for convenience/logging by the caller.
    """
    case_name = os.path.splitext(os.path.basename(filepath))[0]
    model = _get_embedding_model()
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # --- 1. Chunk-level: embed and store each chunk ---
    chunks = chunk_pdf(filepath)

    if chunks:
        chunk_texts = [c["text"] for c in chunks]
        chunk_embeddings = model.encode(chunk_texts).tolist()
        chunk_ids = [f"{case_name}_p{c['page_number']}_{i}" for i, c in enumerate(chunks)]
        chunk_metadatas = [
            {"case_name": c["case_name"], "page_number": c["page_number"]}
            for c in chunks
        ]

        chunks_collection = client.get_or_create_collection(name=CHUNKS_COLLECTION)
        chunks_collection.add(
            ids=chunk_ids,
            embeddings=chunk_embeddings,
            documents=chunk_texts,
            metadatas=chunk_metadatas,
        )

    # --- 2. Case-level: generate, embed, and store the summary ---
    # summarize_case expects {text, page_number} dicts, which chunks already are.
    summary_text = summarize_case(chunks)
    summary_embedding = model.encode([summary_text]).tolist()[0]

    cases_collection = client.get_or_create_collection(name=CASES_COLLECTION)
    cases_collection.add(
        ids=[case_name],
        embeddings=[summary_embedding],
        documents=[summary_text],
        metadatas=[{"case_name": case_name}],
    )

    return case_name


def replace_case(filepath):
    """
    Re-ingest a case from scratch: delete all existing chunks and the
    existing summary for this case_name from "legal_chunks" and
    "legal_cases", then call ingest_new_case() to rebuild them fresh.

    Use this when a case PDF has changed and needs updating, rather than
    ingest_new_case() (which assumes the case is new and would otherwise
    create duplicate records alongside the stale ones).

    Args:
        filepath: path to the case PDF.

    Returns:
        str: the case_name that was replaced/re-ingested.
    """
    case_name = os.path.splitext(os.path.basename(filepath))[0]
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Delete existing chunks for this case, if the collection exists.
    try:
        chunks_collection = client.get_collection(name=CHUNKS_COLLECTION)
        chunks_collection.delete(where={"case_name": case_name})
    except Exception:
        pass  # collection doesn't exist yet -> nothing to delete

    # Delete existing summary for this case, if the collection exists.
    try:
        cases_collection = client.get_collection(name=CASES_COLLECTION)
        cases_collection.delete(where={"case_name": case_name})
    except Exception:
        pass  # collection doesn't exist yet -> nothing to delete

    return ingest_new_case(filepath)


if __name__ == "__main__":
    import sys

    if len(sys.argv) not in (2, 3):
        print("Usage: python ingest.py <path_to_pdf> [--replace]")
        sys.exit(1)

    path = sys.argv[1]
    if len(sys.argv) == 3 and sys.argv[2] == "--replace":
        name = replace_case(path)
        print(f"Replaced case: {name}")
    else:
        name = ingest_new_case(path)
        print(f"Ingested case: {name}")
