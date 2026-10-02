"""Build eval_questions.json from manually reviewed candidates.json."""

import argparse
import json


def _eval_item(candidate):
    """Keep only the fields eval.py needs, validating the review output."""
    item_type = candidate.get("type")
    item = {
        "question": candidate["question"],
        "expected_pages": candidate["expected_pages"],
    }
    if item_type == "single":
        item["expected_case"] = candidate["expected_case"]
    elif item_type == "cross":
        expected_cases = candidate["expected_cases"]
        if len(expected_cases) != 2:
            raise ValueError("Cross-case candidates must contain exactly two expected_cases.")
        item["expected_cases"] = expected_cases
        item["type"] = "cross"
    else:
        raise ValueError("Each candidate must have type 'single' or 'cross'.")
    return item


def main():
    parser = argparse.ArgumentParser(description="Remove review-only text from eval candidates.")
    parser.add_argument("--input", default="candidates.json", help="Reviewed candidates JSON")
    parser.add_argument("--output", default="eval_questions.json", help="Evaluation JSON path")
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as input_file:
        candidates = json.load(input_file)
    if not isinstance(candidates, list):
        raise ValueError("Candidates JSON must be a list.")

    questions = [_eval_item(candidate) for candidate in candidates]
    with open(args.output, "w", encoding="utf-8") as output_file:
        json.dump(questions, output_file, indent=2, ensure_ascii=False)
    print(f"Wrote {len(questions)} evaluation questions to {args.output}")


if __name__ == "__main__":
    main()
