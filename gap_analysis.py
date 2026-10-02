"""Analyze the gap between the first and second Stage 1 case matches."""

import json
import os
import statistics
import sys


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "retrieval")))

from stage1_case_retrieval import get_relevant_cases


THRESHOLDS = (0.02, 0.03, 0.05, 0.08, 0.10)


def _expected_cases(question):
    """Return all acceptable first-place cases for single and cross items."""
    return question.get("expected_cases") or [question.get("expected_case")]


def _print_stats(label, gaps):
    if not gaps:
        print(f"{label}: no questions")
        return

    print(
        f"{label} ({len(gaps)} questions): "
        f"mean={statistics.mean(gaps):.4f}, "
        f"median={statistics.median(gaps):.4f}, "
        f"min={min(gaps):.4f}, max={max(gaps):.4f}"
    )


def main():
    questions_path = "eval_questions.json"
    if not os.path.exists(questions_path):
        print(f"Error: {questions_path} not found. Run from the project root.")
        return

    with open(questions_path, encoding="utf-8") as questions_file:
        questions = json.load(questions_file)

    rows = []
    print("Q# | Top-1 case | Top-1 score | Top-2 case | Top-2 score | Gap | Top-1 correct")
    print("-" * 100)

    for number, question in enumerate(questions, start=1):
        cases = get_relevant_cases(question["question"], top_k=5)
        top_1 = cases[0] if cases else None
        top_2 = cases[1] if len(cases) > 1 else None
        gap = (
            top_1["relevance_score"] - top_2["relevance_score"]
            if top_1 is not None and top_2 is not None
            else None
        )
        correct = top_1 is not None and top_1["case_name"] in _expected_cases(question)
        rows.append({"gap": gap, "correct": correct})

        top_1_name = top_1["case_name"] if top_1 else "None"
        top_1_score = f"{top_1['relevance_score']:.4f}" if top_1 else "N/A"
        top_2_name = top_2["case_name"] if top_2 else "None"
        top_2_score = f"{top_2['relevance_score']:.4f}" if top_2 else "N/A"
        gap_text = f"{gap:.4f}" if gap is not None else "N/A"
        print(
            f"{number:<2} | {top_1_name} | {top_1_score} | {top_2_name} | "
            f"{top_2_score} | {gap_text} | {correct}"
        )

    comparable_rows = [row for row in rows if row["gap"] is not None]
    correct_gaps = [row["gap"] for row in comparable_rows if row["correct"]]
    wrong_gaps = [row["gap"] for row in comparable_rows if not row["correct"]]

    print("\n--- Gap statistics ---")
    _print_stats("Correct top-1", correct_gaps)
    _print_stats("Wrong top-1", wrong_gaps)

    print("\n--- Ambiguity thresholds ---")
    for threshold in THRESHOLDS:
        ambiguous = [row for row in comparable_rows if row["gap"] <= threshold]
        wrong_top_1 = sum(not row["correct"] for row in ambiguous)
        print(
            f"{threshold:.2f}: {len(ambiguous)} ambiguous; "
            f"{wrong_top_1} had a wrong top-1"
        )


if __name__ == "__main__":
    main()
