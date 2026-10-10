"""Run one real query through the full pipeline and print timestamps."""

import os
import sys
import time

# -- Make the subpackages importable --
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
for _folder in ("retrieval", "generation", "routing", "ingestion"):
    _path = os.path.join(PROJECT_ROOT, _folder)
    if _path not in sys.path:
        sys.path.insert(0, _path)

# -- Imports (after path fix) --
from stage1_case_retrieval import get_relevant_cases
from stage2_chunk_retrieval import get_relevant_chunks
from generate import generate_answer
from verifier import verify_answer, generate_verified_answer
from router import decide_mode
from stage2_chunk_retrieval import get_rerank_seconds, reset_rerank_timer

def _cap_chunks_per_case(chunks, per_case=2):
    """Mirror of app.py._cap_chunks_per_case — top-2 per case, then re-sorted."""
    by_case = {}
    for chunk in chunks:
        by_case.setdefault(chunk["case_name"], []).append(chunk)

    capped = []
    for case_chunks in by_case.values():
        case_chunks_sorted = sorted(case_chunks, key=lambda c: c["relevance_score"], reverse=True)
        capped.extend(case_chunks_sorted[:per_case])

    capped.sort(key=lambda c: c["relevance_score"], reverse=True)
    return capped

# -- Question --
question = (
    "What did the Supreme Court establish in the case of Maula Bux v. Union of India "
    "regarding the forfeiture of earnest money when a contract is breached?"
)


def run_query_with_timing(q: str):
    print("Query: %s...\n" % q[:100])
    reset_rerank_timer()

    # -- Stage 1: case retrieval --
    t0 = time.time()
    shortlist = get_relevant_cases(q)
    t1 = time.time()
    print("stage1 (case retrieval) : %.1fs  =>  %d case(s)" % (t1 - t0, len(shortlist)))
    for c in shortlist:
        print("   - %s  (score %.3f)" % (c['case_name'], c['relevance_score']))

    # -- Decide mode --
    mode = decide_mode(shortlist) if shortlist else "fast"
    case_names = [c["case_name"] for c in shortlist]
    print("\nResolved mode: %s  |  using %d case(s)\n" % (mode, len(case_names)))

    # Fast mode: restrict chunk retrieval to the top-ranked case only,
    # mirroring app.py fast-path (shortlisted_cases[0]).
    top_case_names = [shortlist[0]["case_name"]] if shortlist else []
    chunks = get_relevant_chunks(q, top_case_names)
    t2 = time.time()
    print("stage2 (chunk retrieval): %.1fs  =>  %d chunk(s)" % (t2 - t1, len(chunks)))
    print("reranking (included above): %.1fs" % get_rerank_seconds())

    # -- Cap to top-2 per case (mirrors app.py fast-path _cap_chunks) --
    chunks = _cap_chunks_per_case(chunks)
    print("after cap              :           %d chunk(s) kept" % len(chunks))
    print("using case             : %s" % (top_case_names[0] if top_case_names else "n/a"))

    # -- Stage 3: generate answer --
    answer_text = generate_answer(q, chunks, model="qwen2.5:7b-instruct")
    t3 = time.time()
    print("generate (LLM answer)  : %.1fs  =>  %d chars" % (t3 - t2, len(answer_text)))

    # -- Stage 4: verify answer --
    result = verify_answer(answer_text, chunks, model="qwen2.5:7b-instruct", question=q)
    t4 = time.time()
    print("verify                 : %.1fs  =>  verified=%s" % (t4 - t3, result['verified']))
    if not result["verified"]:
        print("   issue: %s" % result.get('issue', 'n/a'))

    # -- Total --
    print("\ntotal wall-clock       : %.1fs" % (t4 - t0))

    # -- Answer --
    print("\n" + "=" * 60)
    print("ANSWER")
    print("=" * 60)
    print(answer_text)


if __name__ == "__main__":
    run_query_with_timing(question)
