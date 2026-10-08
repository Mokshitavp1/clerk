"""
Stage 2 retrieval: given a query and a shortlist of case_names (from Stage 1),
find the most relevant chunks within just those cases.

Returns the contract 3.2 shape from CONTRACTS.md:
    {"text": str, "case_name": str, "page_number": int, "relevance_score": float}
"""

import chromadb
import time
import sys
import numpy as np
from functools import lru_cache

from embeddings import get_embedding_model
from reranker import rerank

CHROMA_PATH = "data/chroma_db"
CHUNKS_COLLECTION = "legal_chunks"

_bm25_index = None
_bm25_corpus = None
_bm25_count = -1

# Module-level rerank timer.  Call reset_rerank_timer() before a query batch
# and get_rerank_seconds() after to read the total wall time spent in rerank
# across all get_relevant_chunks calls since the last reset.  This avoids any
# need for callers to monkeypatch the rerank symbol.
_rerank_seconds = 0.0


@lru_cache(maxsize=1)
def _get_chroma_client():
    """Reuse the persistent client across queries in this process."""
    return chromadb.PersistentClient(path=CHROMA_PATH)


@lru_cache(maxsize=128)
def _get_query_embedding(query):
    """Reuse an embedding when Deep mode searches the same query per case."""
    model = get_embedding_model()
    return tuple(model.encode([query], normalize_embeddings=True)[0].tolist())


def reset_rerank_timer():
    """Reset the accumulated rerank time to zero."""
    global _rerank_seconds
    _rerank_seconds = 0.0


def get_rerank_seconds():
    """Return total seconds spent in rerank since the last reset_rerank_timer() call."""
    return _rerank_seconds

def get_bm25_index(collection):
    global _bm25_index, _bm25_corpus, _bm25_count
    current_count = collection.count()
    if _bm25_index is None or _bm25_count != current_count:
        all_docs = collection.get()
        _bm25_corpus = []
        for i, text in enumerate(all_docs["documents"]):
            _bm25_corpus.append({
                "id": all_docs["ids"][i],
                "text": text,
                "case_name": all_docs["metadatas"][i]["case_name"],
                "page_number": all_docs["metadatas"][i]["page_number"]
            })
        import re
        tokenized = [re.findall(r"\w+", doc["text"].lower()) for doc in _bm25_corpus]
        from rank_bm25 import BM25Okapi
        _bm25_index = BM25Okapi(tokenized)
        _bm25_count = current_count
    return _bm25_index, _bm25_corpus


def get_relevant_chunks(query, case_names, top_k=6, rerank_flag=True):
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

    model = get_embedding_model()
    client = _get_chroma_client()

    try:
        collection = client.get_collection(name=CHUNKS_COLLECTION)
    except Exception:
        return []  # no chunks ingested yet

    if collection.count() == 0:
        return []

    query_embedding_np = np.asarray(_get_query_embedding(query))
    query_embedding = [query_embedding_np.tolist()]

    # Chroma's where clause needs $in for a list of allowed values, even
    # when case_names has only one element.
    where_filter = {"case_name": {"$in": case_names}}

    fetch_k = 12 if rerank_flag else top_k

    dense_results = collection.query(
        query_embeddings=query_embedding,
        n_results=fetch_k,
        where=where_filter,
    )

    union_candidates = {}

    if dense_results["ids"] and dense_results["ids"][0]:
        documents = dense_results["documents"][0]
        metadatas = dense_results["metadatas"][0]
        distances = dense_results["distances"][0]
        ids = dense_results["ids"][0]

        for c_id, text, metadata, distance in zip(ids, documents, metadatas, distances):
            # This is cosine similarity because the collections use hnsw:space=cosine.
            score = max(0.0, min(1.0, 1.0 - distance))
            union_candidates[c_id] = {
                "text": text,
                "case_name": metadata["case_name"],
                "page_number": metadata["page_number"],
                "relevance_score": score,
            }

    # BM25 retrieval
    bm25_index, bm25_corpus = get_bm25_index(collection)
    import re
    tokenized_query = re.findall(r"\w+", query.lower())
    bm25_scores = bm25_index.get_scores(tokenized_query)
    
    bm25_case_docs = []
    for score, doc in zip(bm25_scores, bm25_corpus):
        if doc["case_name"] in case_names:
            bm25_case_docs.append((score, doc))
            
    bm25_case_docs.sort(key=lambda x: x[0], reverse=True)
    
    missing_dense = []
    for score, doc in bm25_case_docs[:fetch_k]:
        c_id = doc["id"]
        if c_id not in union_candidates:
            c = {
                "text": doc["text"],
                "case_name": doc["case_name"],
                "page_number": doc["page_number"],
                "relevance_score": 0.0,
            }
            union_candidates[c_id] = c
            missing_dense.append(c)
            
    if missing_dense and not rerank_flag:
        texts = [c["text"] for c in missing_dense]
        chunk_embeddings = model.encode(texts, normalize_embeddings=True)
        for i, c in enumerate(missing_dense):
            dot = np.dot(query_embedding_np, chunk_embeddings[i])
            c["relevance_score"] = float(max(0.0, min(1.0, dot)))

    relevant_chunks = list(union_candidates.values())
    relevant_chunks.sort(key=lambda c: c["relevance_score"], reverse=True)

    if rerank_flag:
        t0 = time.time()
        relevant_chunks = rerank(query, relevant_chunks, top_n=5)
        _rerank_seconds_delta = time.time() - t0
        global _rerank_seconds
        _rerank_seconds += _rerank_seconds_delta
    else:
        relevant_chunks = relevant_chunks[:top_k]

    return relevant_chunks


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
