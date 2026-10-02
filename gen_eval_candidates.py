"""Generate reviewable retrieval-evaluation candidates from Chroma chunks.

Run with ``python gen_eval_candidates.py``.  The script does not modify the
database or the retrieval pipeline; it writes candidates.json for manual
review.
"""

import argparse
import json
import random
from collections import defaultdict, deque

import chromadb
import ollama


CHROMA_PATH = "data/chroma_db"
CHUNKS_COLLECTION = "legal_chunks"
DEFAULT_MODEL = "qwen2.5:7b-instruct"
SEED = 42

SINGLE_SCHEMA = {
    "type": "object",
    "properties": {"question": {"type": "string"}},
    "required": ["question"],
    "additionalProperties": False,
}


def _word_count(text):
    return len(text.split())


def _ask_question(prompt, model):
    """Ask Ollama for the single JSON field used by candidate records."""
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        format=SINGLE_SCHEMA,
        options={"temperature": 0.7},
    )
    content = response["message"]["content"]
    question = json.loads(content).get("question", "").strip()
    if not question:
        raise ValueError("Ollama returned an empty question")
    return question


def _single_prompt(text):
    return f"""You are a junior lawyer who has NOT read this judgment. Write one
question that this passage answers.

Rules:
- Do not copy distinctive phrases, party names, or section numbers from the passage.
- Paraphrase the passage in your own words.
- The question must be answerable from this passage alone.
- It should sound like a real legal research question, not a reading-comprehension quiz.

Passage:
---
{text}
---"""


def _cross_prompt(first, second):
    return f"""You are a junior lawyer who has NOT read these judgments. Write one
legal research question that requires BOTH passages to answer fully; neither
passage alone should provide the complete answer.

Rules:
- Do not copy distinctive phrases, party names, or section numbers from either passage.
- Paraphrase in your own words.
- The question must be answerable using these two passages together.
- It should sound like a real research question, not a reading-comprehension quiz.

Passage A:
---
{first}
---

Passage B:
---
{second}
---"""


def _sample_round_robin(collection, count, rng):
    """Return up to count eligible chunks, balanced across cases by rounds."""
    records = collection.get(include=["documents", "metadatas"])
    by_case = defaultdict(list)
    for text, metadata in zip(records.get("documents", []), records.get("metadatas", [])):
        if text and metadata and _word_count(text) >= 80:
            by_case[metadata["case_name"]].append(
                {"text": text, "case_name": metadata["case_name"], "page_number": metadata["page_number"]}
            )

    if not by_case:
        raise RuntimeError("No legal_chunks with at least 80 words were found.")

    # Randomising each case's page/chunk order prevents page order from biasing
    # the round-robin sample.  The fixed RNG makes the result reproducible.
    case_names = list(by_case)
    rng.shuffle(case_names)
    queues = {}
    for case_name in case_names:
        rng.shuffle(by_case[case_name])
        queues[case_name] = deque(by_case[case_name])

    chosen = []
    while len(chosen) < count:
        added_this_round = False
        for case_name in case_names:
            if len(chosen) >= count:
                break
            if queues[case_name]:
                chosen.append(queues[case_name].popleft())
                added_this_round = True
        if not added_this_round:
            break
    return chosen


def _write_candidates(candidates, output_path):
    """Checkpoint after every model call so a long Ollama run can resume."""
    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(candidates, output_file, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="Generate manual eval-question candidates.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Ollama model to use")
    parser.add_argument("--output", default="candidates.json", help="Output JSON path")
    args = parser.parse_args()

    rng = random.Random(SEED)
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_collection(name=CHUNKS_COLLECTION)
    sampled = _sample_round_robin(collection, count=24, rng=rng)
    if len(sampled) < 24:
        print(f"Warning: only {len(sampled)} eligible chunks were available.")

    try:
        with open(args.output, encoding="utf-8") as input_file:
            candidates = json.load(input_file)
    except FileNotFoundError:
        candidates = []

    single_candidates = [item for item in candidates if item.get("type") == "single"]
    cross_candidates = [item for item in candidates if item.get("type") == "cross"]
    if len(single_candidates) != len(candidates) - len(cross_candidates):
        raise ValueError("Existing output contains a candidate without a valid type.")
    if cross_candidates and len(single_candidates) < len(sampled):
        raise ValueError("Cannot resume: cross-case candidates precede all single-case candidates.")
    if len(single_candidates) > len(sampled):
        raise ValueError("Cannot resume: output has more single-case candidates than the sample.")

    # Existing candidates are checkpoints from this fixed-seed run.  Resume
    # from the next sampled item rather than repeating already-paid model calls.
    for index, chunk in enumerate(sampled[len(single_candidates):], start=len(single_candidates) + 1):
        print(f"Generating single-case candidate {index}/{len(sampled)}...")
        candidates.append({
            "question": _ask_question(_single_prompt(chunk["text"]), args.model),
            "expected_case": chunk["case_name"],
            "expected_pages": [chunk["page_number"]],
            "source_text": chunk["text"],
            "type": "single",
        })
        _write_candidates(candidates, args.output)

    # Draw pairs from sampled chunks only, always using different cases.
    possible_pairs = [
        (left, right)
        for left_index, left in enumerate(sampled)
        for right in sampled[left_index + 1:]
        if left["case_name"] != right["case_name"]
    ]
    rng.shuffle(possible_pairs)
    desired_cross_count = min(5, len(possible_pairs))
    if len(cross_candidates) > desired_cross_count:
        raise ValueError("Cannot resume: output has too many cross-case candidates.")
    for index, (first, second) in enumerate(
        possible_pairs[len(cross_candidates):desired_cross_count], start=len(cross_candidates) + 1
    ):
        print(f"Generating cross-case candidate {index}/{min(5, len(possible_pairs))}...")
        candidates.append({
            "question": _ask_question(_cross_prompt(first["text"], second["text"]), args.model),
            "expected_cases": [first["case_name"], second["case_name"]],
            "expected_pages": [first["page_number"], second["page_number"]],
            "source_text": [first["text"], second["text"]],
            "type": "cross",
        })
        _write_candidates(candidates, args.output)

    if desired_cross_count < 5:
        print(f"Warning: only {len(possible_pairs)} cross-case pairs were possible.")

    _write_candidates(candidates, args.output)
    print(f"Wrote {len(candidates)} candidates to {args.output}")


if __name__ == "__main__":
    main()
