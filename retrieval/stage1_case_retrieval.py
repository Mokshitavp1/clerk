"""
Stage 1 retrieval: given a query, find the most relevant case summaries.

Returns the contract 3.1 shape from CONTRACTS.md:
    {"case_name": str, "relevance_score": float}  # 0.0-1.0, higher = more relevant
"""

import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_PATH = "data/chroma_db"
CASES_COLLECTION = "legal_cases"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Loaded once per process, not per call.
_embedding_model = None


def _get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedding_model


def get_relevant_cases(query, top_k=5):
    """
    Embed a query and search the "legal_cases" collection for the top_k
    most similar case summaries.

    Args:
        query: the user's natural-language question.
        top_k: how many cases to return, at most (fewer if the collection
            has fewer records than top_k).

    Returns:
        list[dict]: [{"case_name": str, "relevance_score": float}, ...],
        sorted by relevance_score descending. Empty list if the
        collection doesn't exist yet or has no records.
    """
    model = _get_embedding_model()
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    try:
        collection = client.get_collection(name=CASES_COLLECTION)
    except Exception:
        return []  # no cases ingested yet

    if collection.count() == 0:
        return []

    query_embedding = model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(top_k, collection.count()),
    )

    case_names = results["metadatas"][0]
    distances = results["distances"][0]

    relevant_cases = []
    for metadata, distance in zip(case_names, distances):
        # NOTE: Chroma returns a distance, not a similarity, and the exact
        # meaning of "distance" depends on the collection's configured
        # space (defaults to squared L2 unless created with
        # hnsw:space="cosine"). To keep relevance_score in the 0.0-1.0
        # range regardless of which metric was used at collection-creation
        # time, we convert with 1 / (1 + distance): monotonically
        # decreasing in distance, bounded in (0, 1]. This is NOT a true
        # cosine similarity score — if you need that specifically, the
        # "legal_cases" collection must be created with
        # metadata={"hnsw:space": "cosine"} and this should be changed to
        # score = 1 - (distance / 2).
        relevance_score = 1.0 / (1.0 + distance)

        relevant_cases.append({
            "case_name": metadata["case_name"],
            "relevance_score": relevance_score,
        })

    relevant_cases.sort(key=lambda c: c["relevance_score"], reverse=True)

    return relevant_cases


def is_ambiguous(results, threshold=0.1):
    """
    Decide whether the top 2 results are close enough that no single case
    clearly dominates the query.

    Args:
        results: list of dicts as returned by get_relevant_cases(), i.e.
            [{"case_name": str, "relevance_score": float}, ...], assumed
            to already be sorted by relevance_score descending.
        threshold: if the top two relevance_score values differ by this
            much or less, the result is considered ambiguous.

    Returns:
        bool: True if ambiguous (top two scores within threshold of each
        other), False if one result clearly dominates. Also False if
        there are fewer than 2 results, since ambiguity requires at
        least two candidates to compare.
    """
    if len(results) < 2:
        return False

    top_score = results[0]["relevance_score"]
    second_score = results[1]["relevance_score"]

    return (top_score - second_score) <= threshold


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python retrieval_stage1.py '<query>'")
        sys.exit(1)

    cases = get_relevant_cases(sys.argv[1])
    for c in cases:
        print(f"  {c['relevance_score']:.3f}  {c['case_name']}")
    print(f"Ambiguous: {is_ambiguous(cases)}")
