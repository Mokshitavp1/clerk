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

# -- Question --
question = (
    "My client paid an advance to a government contractor for a supply contract, "
    "but before any work was done, the contract was cancelled. The contractor is "
    "refusing to refund the advance, pointing to a clause that lets them keep it if "
    "the deal falls through. Is there a similar case on whether that kind of "
    "forfeiture is valid without proof the government actually suffered a loss? "
    "(Liquidated damages vs. proof of loss - see Saw Pipes and Fateh Chand)"
)


def run_query_with_timing(q: str):
    print("Query: %s...\n" % q[:100])

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

    # -- Stage 2: chunk retrieval --
    chunks = get_relevant_chunks(q, case_names)
    t2 = time.time()
    print("stage2 (chunk retrieval): %.1fs  =>  %d chunk(s)" % (t2 - t1, len(chunks)))

    # -- Stage 3: generate answer --
    answer_text = generate_answer(q, chunks)
    t3 = time.time()
    print("generate (LLM answer)  : %.1fs  =>  %d chars" % (t3 - t2, len(answer_text)))

    # -- Stage 4: verify answer --
    result = verify_answer(answer_text, chunks)
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
