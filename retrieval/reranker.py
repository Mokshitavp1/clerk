import math
import sys

_cross_encoder = None

def get_cross_encoder():
    global _cross_encoder
    if _cross_encoder is None:
        from sentence_transformers import CrossEncoder
        _cross_encoder = CrossEncoder("BAAI/bge-reranker-v2-m3")
    return _cross_encoder

def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))

def rerank(query, chunks, top_n=5):
    """
    Rerank a list of chunk dicts (contract 3.2 shape) for the given query.
    Replaces relevance_score with a 0-1 sigmoid score from the CrossEncoder.
    """
    if not chunks:
        return []
        
    model = get_cross_encoder()
    pairs = [[query, c["text"]] for c in chunks]
    
    scores = model.predict(pairs)
    
    for c, score in zip(chunks, scores):
        c["relevance_score"] = sigmoid(score)
        
    chunks.sort(key=lambda c: c["relevance_score"], reverse=True)
    
    return chunks[:top_n]
