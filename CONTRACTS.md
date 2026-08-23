# CONTRACTS.md — Clerk Interface Contract

> **This document is the shared boundary between Person A (ingestion/parsing) and**
> **Person B (retrieval/generation/UI). Do not change any shape or default below**
> **without flagging both parties first. A silent shape change breaks the other**
> **person's code.**

---

## 1. Model Defaults

| Component | Model | Where used |
|---|---|---|
| LLM for generation | `qwen2.5:7b-instruct` (via Ollama) | `generate.py`, `verifier.py`, `summarizer.py` |
| LLM for verification | `qwen2.5:7b-instruct` (via Ollama) | `verifier.py` |
| LLM for summarization | `qwen2.5:7b-instruct` (via Ollama) | `summarizer.py` |
| Embedding model | `all-MiniLM-L6-v2` (sentence-transformers) | `ingest.py`, `stage1_case_retrieval.py`, `stage2_chunk_retrieval.py` |

**Rule:** If any module changes its model default, it must be updated in this table and in every other module that uses the same model, then flagged to both parties.

---

## 2. ChromaDB Collections

Two persistent collections live in `data/chroma_db/`:

| Collection name | Contents | Owner |
|---|---|---|
| `legal_cases` | One entry per case: the LLM-generated summary embedding | Person A (ingest.py) |
| `legal_chunks` | One entry per chunk: the raw chunk text embedding | Person A (ingest.py) |

**Constants (must match in every file that touches ChromaDB):**
```python
CHROMA_PATH       = "data/chroma_db"
CHUNKS_COLLECTION = "legal_chunks"
CASES_COLLECTION  = "legal_cases"
```

---

## 3. Data Shapes

### 3.1 Case record — `legal_cases` collection metadata

Each record's metadata dict must contain exactly:
```python
{"case_name": str}   # PDF filename without extension, e.g. "Oil_Natural_Gas_Corporation_Ltd_vs_Saw_Pipes_Ltd_on_17_April_2003"
```

`case_name` is derived from the PDF filename: `os.path.splitext(os.path.basename(filepath))[0]`.  
**No path components. No extension. Must be identical in both collections.**

Stage 1 retrieval return shape (from `stage1_case_retrieval.get_relevant_cases`):
```python
[{"case_name": str, "relevance_score": float}, ...]   # sorted descending by relevance_score
```

### 3.2 Chunk record — `legal_chunks` collection metadata + return shape

Each record's metadata dict must contain exactly:
```python
{"case_name": str, "page_number": int}
```

Stage 2 retrieval return shape (from `stage2_chunk_retrieval.get_relevant_chunks`):
```python
[
    {
        "text": str,
        "case_name": str,
        "page_number": int,
        "relevance_score": float,   # 0.0–1.0, higher = more relevant
    },
    ...
]
```
Sorted descending by `relevance_score`. The extra `relevance_score` key is tolerated (ignored) by `generate.py` and `verifier.py`.

Parser output shape (from `parser.chunk_pdf`):
```python
[{"text": str, "case_name": str, "page_number": int}, ...]
```

### 3.3 Self-RAG output shape (from `self_rag.get_graded_cases`)

```python
{
    "cases": [
        {
            "case_name": str,
            "relevance_score": float,
            "chunks": [<chunk dict per 3.2>, ...],
        },
        ...
    ],
    "insufficient_cases": bool,   # True iff cases is empty
}
```

`"cases"` is empty **exactly when** `"insufficient_cases"` is `True`.

### 3.4 Generation output shape (from `verifier.generate_verified_answer`)

```python
{"answer": str, "verified": bool}
```

`verified` is `True` only if the answer passed both deterministic citation check and LLM groundedness check.  
When both generation attempts fail verification, `answer` is the fixed string:
```
"No verified answer could be found in the uploaded documents for this question."
```
and `verified` is `False`.

### 3.5 Warning shape (from `router.build_warning`)

Returns `None` when no warning, or:
```python
{
    "message": str,        # short display line
    "explain_why": str,    # longer explanation naming competing cases + scores
}
```

---

## 4. Chunking Parameters

Defined in `parser.chunk_pdf` and should not be changed without flagging:
```python
target_words  = 200   # approximate word-count ceiling per chunk
overlap_words = 25    # word-count overlap between consecutive chunks on the same page
```

---

## 5. Routing Thresholds

Defined in `router.decide_mode` and `stage1_case_retrieval.is_ambiguous`:
```python
ambiguity_threshold = 0.1   # if top-2 relevance_score difference ≤ this, route to "deep"
relevance_floor     = 0.4   # chunks below this score are dropped in self_rag.grade_chunks
```

---

## 6. Known Issues (as of 2026-08-23)

### 6.1 Stage 1 Summary Quality (Person A's item)
The LLM-generated summaries stored in `legal_cases` are sometimes off-topic (e.g. ONGC Saw Pipes summary discusses "public policy" instead of liquidated damages). This causes the correct case to rank last in Stage 1 retrieval even when the query explicitly names it. See Bug Report in `docs/bug_report_person_a.md`.

### 6.2 `fitz` Import Deprecation (Person A's item)
`parser.py` uses `import fitz`. PyMuPDF ≥ 1.25 prefers `import pymupdf as fitz`. The current version (1.28.2) still works but emits a deprecation warning.
