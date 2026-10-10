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
| Embedding model | `BAAI/bge-m3` (sentence-transformers) | `ingest.py`, `stage1_case_retrieval.py`, `stage2_chunk_retrieval.py` |

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

### 3.4 Generation output shape (from `verifier.generate_verified_answer` and `verifier.generate_verified_answer_per_case`)

```python
{"answer": str, "verified": bool}
```

`verified` is `True` only if the answer passed both deterministic citation check and LLM groundedness check.  
When both generation attempts fail verification, `answer` is the fixed string:
```
"No verified answer could be found in the uploaded documents for this question."
```
and `verified` is `False`.

#### 3.4.1 Per-case variant (`generate_verified_answer_per_case`) — Deep Thinking only

`generate_verified_answer_per_case` takes a `cases` list (CONTRACTS.md 3.3 shape) instead of a flat `chunks` list, and runs `generate_verified_answer` independently per case before combining results.

**"Fail closed per claim" tradeoff:**
- A case whose individual answer fails verification is silently **dropped** from the combined output.
- If **at least one** case passes verification, `verified=True` and `answer` contains only the verified sections, prefixed with `"Regarding <case_name>:\n"`.
- If **no** case passes verification, the function returns the same fixed fallback string as the pooled version, with `verified=False`.
- `verified=True` therefore means: *everything in the answer is verified*, **not** *every shortlisted case contributed a section*. This is intentional — a partial verified answer is more useful than none, and nothing unverified ever surfaces.

**What callers must NOT assume:**
- Do not infer from `verified=True` that all shortlisted cases were represented in the answer.
- The "partially verified" internal state is not exposed in the return dict. Callers that need to know which cases were dropped must be restructured (this shape does not support that).



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

### 6.3 Ollama summary timeout
Case summaries are an optional optimization for stage-1 retrieval. The
summarizer uses a bounded Ollama request (`OLLAMA_SUMMARY_TIMEOUT_SECONDS`,
default 60 seconds) and falls back to a short extractive summary when the
local model is unavailable or too slow. Chunk ingestion still completes, so a
slow local LLM cannot leave a build stuck indefinitely.

### 6.4 Query generation and verification limits
Query generation and verification use bounded Ollama requests. Their limits
can be configured with `OLLAMA_QUERY_TIMEOUT_SECONDS` (default 120) and
`OLLAMA_VERIFIER_TIMEOUT_SECONDS` (default 60). A generation/verification
attempt also has a 240-second budget, configurable with
`OLLAMA_VERIFIED_ANSWER_BUDGET_SECONDS`; when the first attempt reaches that
budget, the retry is skipped and the UI receives the normal verified-answer
fallback instead of waiting indefinitely. Claims copied verbatim from their
cited excerpts pass deterministic grounding before the verifier model is
called, avoiding unnecessary retries for explicitly supported answers.
If a retry is needed, it uses shorter independent limits:
`OLLAMA_RETRY_QUERY_TIMEOUT_SECONDS` defaults to 45 seconds and
`OLLAMA_RETRY_VERIFIER_TIMEOUT_SECONDS` defaults to 30 seconds, so a rejected
first answer cannot block the UI for another full generation cycle.

Cross-encoder reranking is disabled by default for interactive retrieval
because the local `BAAI/bge-reranker-v2-m3` model can take several minutes on
CPU. Dense and BM25 retrieval remain enabled. Set `CLERK_ENABLE_RERANK=1`
before starting Streamlit when reranking quality is preferred over response
time, or pass `rerank_flag=True` to `get_relevant_chunks` for a targeted run.
