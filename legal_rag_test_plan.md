# Legal RAG — Pre-Sale Test Plan

Format per test: **Layer → Test → Dataset/Source → Prompt (if code needed) → File & When to add**

All prompts assume pytest + your existing `fixtures.py` conventions. Where a test needs
real case PDFs, ingest them via `ingest.py` into a scratch `data/chroma_db_test/` path
first — never point tests at your real/demo KB.

---

## Layer 1 — Contract / Unit Tests
*No external dataset needed — these run entirely against `fixtures.py`, so build them now, before Person A's real pipeline is even finished.*

### T1. Stage 1 shape + routing logic
- **Dataset:** `fixtures.py` → `STAGE1_CLEAR`, `STAGE1_AMBIGUOUS` (already in your repo)
- **Prompt:**
  > Write pytest unit tests in `tests/test_router.py` that import `STAGE1_CLEAR` and
  > `STAGE1_AMBIGUOUS` from `fixtures.py` and verify `decide_mode`, `build_confidence_line`,
  > and `build_warning` against them. Assert the exact output shapes defined in
  > `CONTRACTS.md` sections 3.1 and 3.5 (including the `None` case for `build_warning`
  > when not ambiguous).
- **When to add:** Now. Depends only on committed fixtures, not on Person A's ChromaDB code.

### T2. Graded-cases contract shape
- **Dataset:** `fixtures.py` → `GRADED_CASES_OK`, `GRADED_CASES_INSUFFICIENT`
- **Prompt:**
  > Write pytest tests in `tests/test_self_rag.py` that monkeypatch
  > `stage1_case_retrieval.get_relevant_cases` and `stage2_chunk_retrieval.get_relevant_chunks`
  > to return fixture data, then assert `self_rag.get_graded_cases` returns exactly the
  > `{"cases": [...], "insufficient_cases": bool}` shape from `CONTRACTS.md` 3.3, including
  > the empty-cases-iff-insufficient invariant.
- **When to add:** As soon as `self_rag.py`'s retry logic is stable — no real ChromaDB needed.

### T3. Verifier parsing + pass/fail behavior
- **Dataset:** `fixtures.py` → `SUPPORTED_ANSWER_TEXT`, `UNSUPPORTED_ANSWER_TEXT`, `CHUNKS_SMITH`
- **Prompt:**
  > Write pytest tests in `tests/test_verifier.py` covering `_parse_verification_response`
  > for well-formed yes/no responses and malformed/unparseable ones (must default to
  > `verified=False`). Then test `verify_answer` end-to-end against `SUPPORTED_ANSWER_TEXT`
  > and `UNSUPPORTED_ANSWER_TEXT` using `CHUNKS_SMITH`, asserting the correct verdict on each.
- **When to add:** As soon as `verifier.py` is code-complete. Requires Ollama running locally
  (`qwen2.5:7b-instruct` pulled) since this calls the real model, not a mock.

---

## Layer 2 — Retrieval Quality (Precision / Recall / MRR)
*Needs a real, populated KB — add only after `ingest.py` has been run against real PDFs.*

### T4. Precision/recall/MRR on your own KB
- **Dataset:** [CourtListener](https://www.courtlistener.com/) — pull ~30–50 real opinion
  PDFs across 4–5 legal topics, then hand-write 20–30 `(query, expected_case_names)` pairs.
- **Prompt:**
  > Write `eval/test_retrieval_quality.py` that loads a JSON file of `(query,
  > expected_case_names)` pairs, runs each through `get_relevant_cases` and
  > `get_relevant_chunks`, and computes precision@k, recall@k, and MRR. Fail the test run
  > if any metric drops below a configurable threshold (e.g. recall@5 ≥ 0.8).
- **When to add:** After `ingest.py` has populated a real test KB (post `CONTRACTS.md` §5
  ingestion step) — this cannot run against fixtures alone.

### T5. Expanded gold-set retrieval benchmark (case law only)
- **Dataset:** [CourtListener](https://www.courtlistener.com/) — scale T4's hand-labeled
  set up to 60–100 `(query, expected_case_names)` pairs across more topics, once you have
  time. There is no clean off-the-shelf *retrieval* benchmark for case law the way
  LegalBench-RAG exists for contracts — [COLIEE](https://sites.ualberta.ca/~rabelo/COLIEE2024/)
  (case law retrieval + entailment) is the closest thing, but it's a competition dataset
  with registration/access friction, so treat it as optional rather than a required layer.
- **Prompt:**
  > Extend `eval/test_retrieval_quality.py`'s query set to 60–100 pairs spanning more legal
  > topics and jurisdictions, and add a breakdown by topic so you can see if precision/recall
  > holds evenly or collapses on specific case types (e.g. contract disputes vs. tort vs.
  > constitutional law).
- **When to add:** Ongoing — grow this alongside T4 as your real KB grows, rather than as a
  one-time benchmark run.

---

## Layer 3 — Faithfulness / Hallucination Testing
*This is the highest-priority layer given you're selling a legal tool.*

### T6. Adversarial verifier stress test
- **Dataset:** `fixtures.py` `UNSUPPORTED_ANSWER_TEXT` as a starting template + hand-written
  adversarial answers (no external dataset — you're authoring the bad answers deliberately).
- **Prompt:**
  > Extend `tests/test_verifier.py` with a parametrized adversarial set: (a) correct facts
  > but a citation pointing to the wrong page, (b) a real citation but a misstated holding,
  > (c) a fabricated dollar figure not present in any chunk, (d) plausible legal reasoning
  > with zero grounding in the provided chunks. Assert `verified=False` on every case, and
  > separately track false-positive rejections (correct answers marked unverified) using
  > `SUPPORTED_ANSWER_TEXT` variants.
- **When to add:** Immediately after T3, before any sales demo — this is your core liability
  defense.

### T7. Expert-labeled groundedness check (real case law)
- **Dataset:** [CaseHOLD](https://huggingface.co/casehold) — 53,000+ real US case law
  citations, each with the correct holding statement plus 4 plausible-but-wrong distractor
  holdings, built from the Harvard case law corpus (repo:
  [github.com/reglab/casehold](https://github.com/reglab/casehold), paper:
  [arXiv:2104.08671](https://arxiv.org/abs/2104.08671)).
- **Prompt:**
  > Write `eval/test_groundedness_casehold.py` that samples CaseHOLD entries, treats each
  > citing-text excerpt as a retrieved chunk, and for each of the 5 candidate holding
  > statements (1 correct + 4 distractors), asks `generate_answer` to state "does this
  > excerpt support this holding?" then runs the result through `verify_answer`. Assert the
  > verifier agrees with CaseHOLD's ground truth: passes the correct holding as grounded,
  > and flags the 4 distractors as unsupported.
- **When to add:** Once `generate.py`/`verifier.py` are both stable — this is your strongest
  evidence for a buyer that the verifier actually distinguishes real holdings from
  plausible-sounding wrong ones, using real case law rather than contract clauses.

---

## Layer 4 — Adversarial / Edge Cases

### T8. No relevant case in KB
- **Dataset:** Your own scratch KB (empty or off-topic) — no external dataset needed.
- **Prompt:**
  > Write `tests/test_edge_cases.py::test_no_relevant_case` that queries a KB containing no
  > relevant case and asserts `get_graded_cases` returns `insufficient_cases=True`, and that
  > `app.py`'s `_run_query` returns the "no sufficient, relevant cases" message rather than
  > any fabricated answer.
- **When to add:** After `self_rag.py` and `app.py`'s `_run_query` wiring are both complete.

### T9. Scanned / corrupted PDFs
- **Dataset:** [CourtListener](https://www.courtlistener.com/) — search pre-1990 opinions,
  which are more likely to be scanned/OCR'd PDFs; pair with a deliberately truncated/corrupted
  PDF file you create yourself.
- **Prompt:**
  > Write `tests/test_parser_edge_cases.py` that runs `parser.chunk_pdf` against (a) a real
  > scanned/OCR'd opinion PDF and (b) a corrupted/truncated PDF file. Assert it either extracts
  > degraded-but-non-empty text, or raises a clear, caught exception — never silently produces
  > empty or garbage chunks that would flow downstream undetected.
- **When to add:** Once `parser.py` is finalized, before the demo — use 2–3 real
  CourtListener PDFs as committed test fixtures.

### T10. Long-document summarization truncation
- **Dataset:** [CourtListener](https://www.courtlistener.com/) — filter for long appellate
  opinions (30+ pages / 8000+ words).
- **Prompt:**
  > Write `tests/test_summarizer_truncation.py` that runs `build_summary_prompt` against a
  > real case exceeding `WORD_LIMIT`, asserting the truncation marker appears, and manually
  > (or via a second LLM call) checks whether the truncated summary still captures the case's
  > holding/outcome — flagging if the truncation cuts off before the holding is stated.
- **When to add:** Once you decide how to resolve the truncation item currently on your open
  list — write the test first so you can measure the fix's effect.

---

## Layer 5 — Regression / Snapshot Testing

### T11. Golden snapshot suite
- **Dataset:** A fixed, curated set of ~10–15 real cases from
  [CourtListener](https://www.courtlistener.com/), ingested once and never changed —
  this becomes your permanent regression corpus.
- **Prompt:**
  > Write `tests/test_regression_snapshots.py` that runs a fixed list of ~15 queries
  > end-to-end (retrieval rankings + verified answers) against the golden KB, and diffs the
  > output against stored JSON snapshots in `snapshots/`. Fail loudly on any drift, and
  > provide a `--update-snapshots` flag for intentional changes.
- **When to add:** Right after your v2 UI and pipeline are both locked. Re-run this suite
  before and after every subsequent prompt, model, or chunking change from then on — this is
  the direct fix for the incremental-prompt-collision failure mode you already hit once with
  the CSS regression.

---

## Layer 6 — Load / Environment Testing

### T12. Bulk ingestion load test
- **Dataset:** [CourtListener bulk data](https://wiki.free.law/c/courtlistener/help/api/bulk-data/bulk-legal-data)
  or [Caselaw Access Project on Hugging Face](https://huggingface.co/datasets/free-law/Caselaw_Access_Project)
  — pull 200–500 real PDFs for volume.
- **Prompt:**
  > Write `scripts/load_test_ingest.py` that sequentially ingests 200–500 real case PDFs
  > through `ingest.py`, logging per-document time, peak memory, and any failures, to
  > characterize how ingestion scales on the actual demo/sale machine. Also test what state
  > `data/chroma_db/` is left in if the process is killed mid-run, given `replace_case` is
  > non-atomic.
- **When to add:** Last — right before the `CONTRACTS.md` §5 integration checklist / demo,
  once every other layer above already passes.

---

## Suggested run order
1. T1–T3 (now, no dependencies)
2. T8 (as soon as `_run_query` wiring exists)
3. T9, T10 (as `parser.py`/`summarizer.py` finalize)
4. T6 (before any external demo — highest priority for a sellable legal product)
5. T4 (once a real test KB exists)
6. T11 (once v2 UI/pipeline lock — then keep re-running forever)
7. T5, T7 (benchmarking/credibility layer, can run in parallel with the above once stable)
8. T12 (final, pre-sale)
