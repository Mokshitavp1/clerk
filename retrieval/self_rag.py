"""
Self-RAG orchestration: Stage 1 shortlist -> per-case Stage 2 retrieval ->
grading -> retry-with-wider-shortlist if too few cases survive.

Returns the contract 3.3 shape from CONTRACTS.md:
    {
        "cases": [
            {"case_name": str, "relevance_score": float, "chunks": [<chunk dict>, ...]},
            ...
        ],
        "insufficient_cases": bool,
    }
"""

from stage1_case_retrieval import get_relevant_cases
from retrieval_stage2 import get_relevant_chunks
from grade_chunks import grade_chunks


def get_graded_cases(query, initial_top_k=5, min_cases_required=2):
    """
    Run the full Stage 1 -> Stage 2 -> grading pipeline for a query, with
    one automatic retry (doubled Stage 1 top_k) if too few cases survive
    grading the first time.

    Args:
        query: the user's natural-language question.
        initial_top_k: how many cases Stage 1 shortlists on the first try.
        min_cases_required: minimum number of cases that must have at
            least one surviving (post-grading) chunk for the result to be
            considered sufficient.

    Returns:
        dict: {"cases": [...], "insufficient_cases": bool} per
        CONTRACTS.md 3.3. "cases" is empty exactly when
        insufficient_cases is True.
    """
    top_k = initial_top_k

    # Attempt 1: initial_top_k. Attempt 2 (if needed): initial_top_k * 2.
    # "Re-call Stage 1 once" means exactly one retry, not open-ended looping.
    for attempt in range(2):
        stage1_results = get_relevant_cases(query, top_k=top_k)

        surviving_cases = []
        for case in stage1_results:
            case_name = case["case_name"]

            chunks = get_relevant_chunks(query, [case_name])
            graded_chunks, _dropped_count_per_case = grade_chunks(chunks)

            if graded_chunks:
                surviving_cases.append({
                    "case_name": case_name,
                    "relevance_score": case["relevance_score"],
                    "chunks": graded_chunks,
                })

        if len(surviving_cases) >= min_cases_required:
            return {"cases": surviving_cases, "insufficient_cases": False}

        top_k *= 2  # only takes effect if we loop again (attempt 0 -> 1)

    return {"cases": [], "insufficient_cases": True}


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python self_rag.py '<query>'")
        sys.exit(1)

    result = get_graded_cases(sys.argv[1])

    if result["insufficient_cases"]:
        print("Insufficient cases found.")
    else:
        for case in result["cases"]:
            print(f"{case['case_name']} (score={case['relevance_score']:.3f}, "
                  f"{len(case['chunks'])} surviving chunks)")
