"""
Stage 1 retrieval: given a query, find the most relevant case summaries.

Returns the contract 3.1 shape from CONTRACTS.md:
    {"case_name": str, "relevance_score": float}  # 0.0-1.0, higher = more relevant
"""

import chromadb
from functools import lru_cache

from embeddings import get_embedding_model

CHROMA_PATH = "data/chroma_db"
CASES_COLLECTION = "legal_cases"


@lru_cache(maxsize=1)
def _get_chroma_client():
    """Reuse the persistent client across queries in this process."""
    return chromadb.PersistentClient(path=CHROMA_PATH)


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
    model = get_embedding_model()
    client = _get_chroma_client()

    try:
        collection = client.get_collection(name=CASES_COLLECTION)
    except Exception:
        return []  # no cases ingested yet

    if collection.count() == 0:
        return []

    query_embedding = model.encode([query], normalize_embeddings=True).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(top_k, collection.count()),
    )

    case_names = results["metadatas"][0]
    distances = results["distances"][0]

    relevant_cases = []
    for metadata, distance in zip(case_names, distances):
        # This is cosine similarity because the collections use hnsw:space=cosine.
        relevance_score = max(0.0, min(1.0, 1.0 - distance))

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
