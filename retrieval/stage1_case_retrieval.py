"""
Stage 1 retrieval: given a query, find the most relevant case summaries.

Returns the contract 3.1 shape from CONTRACTS.md:
    {"case_name": str, "relevance_score": float}  # 0.0-1.0, higher = more relevant
"""

import chromadb
from functools import lru_cache
from copy import deepcopy
import re

from embeddings import get_embedding_model

CHROMA_PATH = "data/chroma_db"
CASES_COLLECTION = "legal_cases"
_results_cache = {}
_results_cache_count = None


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
    client = _get_chroma_client()

    try:
        collection = client.get_collection(name=CASES_COLLECTION)
    except Exception:
        return []  # no cases ingested yet

    collection_count = collection.count()
    if collection_count == 0:
        return []

    global _results_cache_count
    if _results_cache_count != collection_count:
        _results_cache.clear()
        _results_cache_count = collection_count

    cache_key = (query, top_k)
    if cache_key in _results_cache:
        return deepcopy(_results_cache[cache_key])

    model = get_embedding_model()
    query_embedding = model.encode([query], normalize_embeddings=True).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(top_k, collection_count),
    )

    case_names = results["metadatas"][0]
    distances = results["distances"][0]

    relevant_cases_by_name = {}
    for metadata, distance in zip(case_names, distances):
        # This is cosine similarity because the collections use hnsw:space=cosine.
        relevance_score = max(0.0, min(1.0, 1.0 - distance))
        relevant_cases_by_name[metadata["case_name"]] = {
            "case_name": metadata["case_name"],
            "relevance_score": relevance_score,
        }

    # Dense summary embeddings can miss a case explicitly named by the user.
    # Add exact filename-token matches before truncating to top_k; this does
    # not weaken evidence checks and only improves authority selection.
    all_metadata = collection.get().get("metadatas", [])
    for metadata in all_metadata:
        case_name = metadata["case_name"]
        lexical_score = _case_name_match_score(query, case_name)
        if lexical_score >= 0.5:
            current = relevant_cases_by_name.get(case_name)
            if current is None or lexical_score > current["relevance_score"]:
                relevant_cases_by_name[case_name] = {
                    "case_name": case_name,
                    "relevance_score": lexical_score,
                }

    relevant_cases = list(relevant_cases_by_name.values())
    relevant_cases.sort(key=lambda c: c["relevance_score"], reverse=True)
    relevant_cases = relevant_cases[:top_k]

    _results_cache[cache_key] = deepcopy(relevant_cases)
    return relevant_cases


def clear_retrieval_cache():
    """Clear cached Stage 1 results after an index mutation."""
    global _results_cache_count
    _results_cache.clear()
    _results_cache_count = None


def _case_name_match_score(query, case_name):
    """Score meaningful query-token overlap with a stored case filename."""
    stop_words = {
        "what", "when", "where", "which", "does", "does", "under", "section",
        "contract", "case", "regarding", "according", "the", "and", "for",
    }
    query_tokens = {
        token for token in re.findall(r"[a-z0-9]+", query.lower())
        if len(token) > 2 and token not in stop_words
    }
    case_tokens = {
        token for token in re.findall(r"[a-z0-9]+", case_name.lower().replace("_", " "))
        if len(token) > 2 and token not in stop_words
    }
    if not query_tokens or not case_tokens:
        return 0.0
    return len(query_tokens & case_tokens) / len(case_tokens)


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
