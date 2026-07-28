"""
Stage 2 retrieval: given a query and a shortlist of case_names (from Stage 1),
find the most relevant chunks within just those cases.

Returns the contract 3.2 shape from CONTRACTS.md:
    {"text": str, "case_name": str, "page_number": int, "relevance_score": float}
"""

import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_PATH = "data/chroma_db"
CHUNKS_COLLECTION = "legal_chunks"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Loaded once per process, not per call.
_embedding_model = None


def _get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedding_model


def get_relevant_chunks(query, case_names, top_k=6):
    """
    Embed a query and search the "legal_chunks" collection for the top_k
    most similar chunks, restricted to chunks whose case_name metadata is
    in case_names.

    Args:
        query: the user's natural-language question.
        case_names: list of case_name strings to restrict the search to
            (typically the cases selected by Stage 1 / get_relevant_cases).
        top_k: how many chunks to return, at most.

    Returns:
        list[dict]: [{"text", "case_name", "page_number", "relevance_score"}, ...],
        sorted by relevance_score descending. Empty list if the collection
        doesn't exist, has no records, or case_names is empty.
    """
    if not case_names:
        return []

    model = _get_embedding_model()
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    try:
        collection = client.get_collection(name=CHUNKS_COLLECTION)
    except Exception:
        return []  # no chunks ingested yet

    if collection.count() == 0:
        return []

    query_embedding = model.encode([query]).tolist()

    # Chroma's where clause needs $in for a list of allowed values, even
    # when case_names has only one element.
    where_filter = {"case_name": {"$in": case_names}}

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        where=where_filter,
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    relevant_chunks = []
    for text, metadata, distance in zip(documents, metadatas, distances):
        # Same distance -> similarity conversion used in get_relevant_cases,
        # for consistency across both retrieval stages. See that function's
        # comment for the caveat about Chroma's default distance metric
        # (squared L2 unless the collection was created with
        # hnsw:space="cosine").
        relevance_score = 1.0 / (1.0 + distance)

        relevant_chunks.append({
            "text": text,
            "case_name": metadata["case_name"],
            "page_number": metadata["page_number"],
            "relevance_score": relevance_score,
        })

    relevant_chunks.sort(key=lambda c: c["relevance_score"], reverse=True)

    return relevant_chunks[:top_k]


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python retrieval_stage2.py '<query>' <case_name> [<case_name> ...]")
        sys.exit(1)

    q = sys.argv[1]
    names = sys.argv[2:]

    chunks = get_relevant_chunks(q, names)
    for c in chunks:
        preview = c["text"][:80].replace("\n", " ")
        print(f"  {c['relevance_score']:.3f}  [{c['case_name']} p.{c['page_number']}] {preview}...")
