"""
T11 — Golden snapshot regression suite.

Runs a fixed list of real queries against your golden KB end-to-end
(retrieval + verified answer) and diffs the result against stored JSON
snapshots. Catches silent regressions from prompt tweaks, chunking
changes, or model swaps -- the exact failure mode that caused the CSS
regression earlier in this project's UI work, applied to the RAG pipeline
instead of the UI.

ONE-TIME SETUP (on your machine, with your golden KB already ingested):
    1. Pick ~15 real queries you know the golden KB should answer well.
       Put them in tests/golden_queries.json as a plain list of strings.
    2. Run with --update-snapshots once to create the initial baseline:
           python tests/test_regression_snapshots.py --update-snapshots
    3. Commit snapshots/*.json to git -- this IS your regression baseline.

NORMAL USE (before/after any change):
    pytest tests/test_regression_snapshots.py -v

This cannot run meaningfully without a real, populated, UNCHANGING golden
KB and a real Ollama model -- there's no way to fake this with fixtures,
since the entire point is catching drift in real retrieval + generation
behavior over time.
"""

import sys
import os
import json
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
GOLDEN_QUERIES_PATH = os.path.join(HERE, "golden_queries.json")
SNAPSHOTS_DIR = os.path.join(HERE, "..", "snapshots")


def _load_golden_queries():
    if not os.path.exists(GOLDEN_QUERIES_PATH):
        return []
    with open(GOLDEN_QUERIES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _snapshot_path(query_index):
    return os.path.join(SNAPSHOTS_DIR, f"query_{query_index:03d}.json")


def _run_query_for_snapshot(query):
    """Mirrors app.py's _run_query pipeline, minus the Streamlit UI calls."""
    from stage1_case_retrieval import get_relevant_cases
    from self_rag import get_graded_cases
    from verifier import generate_verified_answer
    from router import decide_mode

    shortlisted = get_relevant_cases(query)
    mode = decide_mode(shortlisted)

    if mode == "fast":
        from stage2_chunk_retrieval import get_relevant_chunks
        case_names = [shortlisted[0]["case_name"]] if shortlisted else []
        chunks = get_relevant_chunks(query, case_names)
    else:
        graded = get_graded_cases(query)
        if graded["insufficient_cases"]:
            return {
                "mode": mode,
                "shortlisted_cases": [c["case_name"] for c in shortlisted],
                "answer": None,
                "verified": False,
                "insufficient": True,
            }
        chunks = [chunk for case in graded["cases"] for chunk in case["chunks"]]

    result = generate_verified_answer(query, chunks)
    return {
        "mode": mode,
        "shortlisted_cases": [c["case_name"] for c in shortlisted],
        "answer": result["answer"],
        "verified": result["verified"],
        "insufficient": False,
    }


def update_snapshots():
    queries = _load_golden_queries()
    if not queries:
        print(f"No queries found at {GOLDEN_QUERIES_PATH}. Populate it first.")
        return
    os.makedirs(SNAPSHOTS_DIR, exist_ok=True)
    for i, query in enumerate(queries):
        print(f"Running query {i}: {query!r}")
        result = _run_query_for_snapshot(query)
        with open(_snapshot_path(i), "w", encoding="utf-8") as f:
            json.dump({"query": query, "result": result}, f, indent=2)
    print(f"Wrote {len(queries)} snapshots to {SNAPSHOTS_DIR}")


@pytest.mark.requires_ollama
class TestGoldenSnapshots:
    """Parametrized dynamically against whatever's in golden_queries.json."""

    @pytest.mark.skipif(
        not os.path.exists(GOLDEN_QUERIES_PATH),
        reason=f"No golden_queries.json at {GOLDEN_QUERIES_PATH} yet.",
    )
    def test_snapshots_directory_exists(self):
        assert os.path.isdir(SNAPSHOTS_DIR), (
            "No snapshots/ directory found -- run "
            "`python tests/test_regression_snapshots.py --update-snapshots` once first."
        )

    @pytest.mark.skipif(
        not os.path.exists(GOLDEN_QUERIES_PATH) or not os.path.isdir(SNAPSHOTS_DIR),
        reason="Golden queries or snapshots not set up yet.",
    )
    @pytest.mark.parametrize("query_index", range(len(_load_golden_queries())))
    def test_query_matches_snapshot(self, query_index):
        queries = _load_golden_queries()
        query = queries[query_index]
        snapshot_path = _snapshot_path(query_index)

        if not os.path.exists(snapshot_path):
            pytest.skip(f"No snapshot yet for query {query_index}: {query!r}")

        with open(snapshot_path, "r", encoding="utf-8") as f:
            expected = json.load(f)["result"]

        actual = _run_query_for_snapshot(query)

        # Mode and which cases got shortlisted should be stable -- if these
        # drift, retrieval itself changed, which is worth knowing about
        # before even looking at the generated answer text.
        assert actual["mode"] == expected["mode"], (
            f"Mode drifted for {query!r}: was {expected['mode']}, now {actual['mode']}"
        )
        assert actual["shortlisted_cases"] == expected["shortlisted_cases"], (
            f"Shortlisted cases drifted for {query!r}"
        )
        assert actual["verified"] == expected["verified"], (
            f"Verification outcome drifted for {query!r}: "
            f"was {expected['verified']}, now {actual['verified']}"
        )
        # Answer text isn't asserted for exact equality -- LLM phrasing
        # varies run to run even with no code changes. Flag it for manual
        # review instead of hard-failing on wording differences.
        if actual["answer"] != expected["answer"]:
            print(
                f"\n[INFO] Answer text differs for {query!r} (not a hard failure):\n"
                f"  was: {expected['answer']}\n"
                f"  now: {actual['answer']}"
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--update-snapshots", action="store_true")
    args = parser.parse_args()
    if args.update_snapshots:
        update_snapshots()
    else:
        print("Run with --update-snapshots to create/refresh the baseline, "
              "or use `pytest tests/test_regression_snapshots.py` to check against it.")
