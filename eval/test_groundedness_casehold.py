"""
T7 — Expert-labeled groundedness check, using real case law (CaseHOLD).

CaseHOLD (https://huggingface.co/casehold) is 53,000+ real US case-law
citations. Each item has:
    - citing_prompt: an excerpt from a real judicial opinion, citing another
      case, with the holding statement masked out as <HOLDING>
    - holding_0..holding_4: five candidate holding statements
    - label: index (0-4) of the correct holding

This test treats each citing_prompt as if it were a retrieved chunk, and
each candidate holding as a claim your system might generate. It checks
whether verify_answer agrees with CaseHOLD's ground truth: the correct
holding should verify as grounded, the four distractors should not.

This is the closest thing to a real, expert-labeled "did the model correctly
distinguish the real holding from a plausible-sounding wrong one" test for
your actual domain (case law), as opposed to contract clauses.

Setup (one-time, on your machine — NOT in a sandbox without internet):
    pip install datasets --break-system-packages

Run:
    python eval/test_groundedness_casehold.py --n 50

Requires:
    - Internet access to huggingface.co (to download the CaseHOLD split)
    - `ollama serve` running locally with qwen2.5:7b-instruct pulled
"""

import argparse
import sys
import os
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "generation"))

from verifier import verify_answer


def _build_pseudo_chunk(citing_prompt, case_id):
    """Wrap a CaseHOLD citing_prompt in your chunk shape (CONTRACTS.md 3.2)
    so it can be passed straight into verify_answer."""
    return {
        "text": citing_prompt,
        "case_name": f"casehold_{case_id}",
        "page_number": 1,
        "relevance_score": 1.0,
    }


def _build_answer_text(holding_text, case_id):
    """Wrap a candidate holding in the same {answer text + Sources: line}
    shape your generate_answer produces, since verify_answer expects that
    format."""
    return f"{holding_text}\n\nSources: casehold_{case_id}, p. 1"


def run_eval(n_samples, seed=42):
    try:
        from datasets import load_dataset
    except ImportError:
        print("Missing dependency. Run: pip install datasets --break-system-packages")
        sys.exit(1)

    print(f"Loading CaseHOLD (test split) from Hugging Face...")
    dataset = load_dataset("casehold/casehold", split="test", trust_remote_code=True)

    random.seed(seed)
    indices = random.sample(range(len(dataset)), min(n_samples, len(dataset)))

    correct_holding_passed = 0
    correct_holding_total = 0
    distractor_rejected = 0
    distractor_total = 0

    for i, idx in enumerate(indices):
        item = dataset[idx]
        citing_prompt = item["citing_prompt"]
        correct_label = item["label"]
        case_id = f"{idx}"

        chunk = _build_pseudo_chunk(citing_prompt, case_id)

        for holding_idx in range(5):
            holding_text = item[f"holding_{holding_idx}"]
            answer_text = _build_answer_text(holding_text, case_id)
            result = verify_answer(answer_text, [chunk])

            if holding_idx == correct_label:
                correct_holding_total += 1
                if result["verified"]:
                    correct_holding_passed += 1
            else:
                distractor_total += 1
                if not result["verified"]:
                    distractor_rejected += 1

        if (i + 1) % 10 == 0:
            print(f"  ...processed {i + 1}/{len(indices)} cases")

    print("\n--- Results ---")
    print(
        f"Correct holdings passed as grounded: "
        f"{correct_holding_passed}/{correct_holding_total} "
        f"({100 * correct_holding_passed / max(correct_holding_total, 1):.1f}%)"
    )
    print(
        f"Distractor holdings correctly rejected: "
        f"{distractor_rejected}/{distractor_total} "
        f"({100 * distractor_rejected / max(distractor_total, 1):.1f}%)"
    )
    print(
        "\nInterpretation: the first number should be high (verifier accepts "
        "real holdings), the second should also be high (verifier rejects "
        "plausible-but-wrong holdings). A low second number means your "
        "verifier is too permissive — the exact failure mode that matters "
        "most for a tool lawyers will rely on."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=50, help="Number of CaseHOLD cases to sample")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    run_eval(args.n, seed=args.seed)
