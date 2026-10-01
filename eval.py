import sys
import os
import json
import time
import hashlib
import argparse
from datetime import datetime

# Add internal modules to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'retrieval')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'generation')))

from stage1_case_retrieval import get_relevant_cases
from stage2_chunk_retrieval import get_relevant_chunks
from verifier import generate_verified_answer


def _sha1_file(path):
    """Return the SHA-1 hex digest of a file's raw bytes."""
    h = hashlib.sha1()
    with open(path, 'rb') as fh:
        h.update(fh.read())
    return h.hexdigest()


def _check_cites_expected(answer_text, expected_case, expected_pages):
    """
    Return True iff the answer's Sources/citations line contains a substring
    matching expected_case AND at least one integer from expected_pages.

    Operates on the plain answer text (no markup).  Returns False for
    empty, abstained, or unverified answers.
    """
    if not answer_text:
        return False
    # Only look at the Sources: line
    sources_line = None
    for line in answer_text.splitlines():
        if line.strip().lower().startswith("sources:"):
            sources_line = line
            break
    if not sources_line:
        return False

    # Normalise for comparison the same way verifier does
    norm_case = expected_case.lower().replace("_", " ")
    norm_sources = sources_line.lower().replace("_", " ")

    case_found = norm_case in norm_sources
    page_found = any(
        f"p. {pg}" in norm_sources or f"p.{pg}" in norm_sources
        for pg in expected_pages
    )
    return case_found and page_found


def run_eval(full_mode=False, model=None, group=None):
    questions_file = "eval_questions.json"
    if not os.path.exists(questions_file):
        print(f"Error: {questions_file} not found. Please create it or run from the correct directory.")
        return

    with open(questions_file, 'r') as f:
        questions = json.load(f)

    # SHA-1 of eval_questions.json — stored in each result file so the
    # comparison table can reject runs built from a different question set.
    questions_hash = _sha1_file(questions_file)

    # Default run_group to today's date (YYYY-MM-DD) when not supplied.
    if group is None:
        group = datetime.now().strftime("%Y-%m-%d")

    default_model = "qwen2.5:7b-instruct"
    effective_model = model if model else default_model

    # ------------------------------------------------------------------
    # Warm-up: one throwaway call before timing starts (--full mode only).
    # This ensures the model weights are resident in Ollama so that the
    # first real question isn't penalised with a cold-start load time.
    # ------------------------------------------------------------------
    if full_mode and questions:
        print(f"[warm-up] Running throwaway generation on Q1 to prime model '{effective_model}'…")
        _warmup_cases = get_relevant_cases(questions[0]['question'], top_k=5)
        _warmup_case_names = [c['case_name'] for c in _warmup_cases]
        _warmup_chunks = get_relevant_chunks(questions[0]['question'], _warmup_case_names, top_k=6)
        if _warmup_chunks:
            try:
                if model:
                    generate_verified_answer(questions[0]['question'], _warmup_chunks, model=model)
                else:
                    generate_verified_answer(questions[0]['question'], _warmup_chunks)
            except Exception:
                pass  # warm-up failures are non-fatal
        print("[warm-up] Done.\n")

    results = []

    # Print table header
    header = f"{'Q#':<3} | {'Top-1 Case OK':<13} | {'Page OK (Top-6)':<15} | {'Scores (Top-6)':<35}"
    if full_mode:
        header += f" | {'Verified':<8} | {'Cites OK':<8} | {'Time (s)':<8} | {'Retries':<7} | {'Chunks':<6} | {'Ans Wds':<7}"
    print(header)
    print("-" * len(header))

    for i, q in enumerate(questions):
        question_text = q['question']
        expected_case = q['expected_case']
        expected_pages = q['expected_pages']

        # ---------------------------
        # 1. Retrieval Only
        # ---------------------------
        cases = get_relevant_cases(question_text, top_k=5)
        top_1_case = cases[0]['case_name'] if cases else None
        case_ok = (top_1_case == expected_case)

        # Get chunks for the retrieved cases
        case_names = [c['case_name'] for c in cases]
        chunks = get_relevant_chunks(question_text, case_names, top_k=6)

        scores = [round(c['relevance_score'], 3) for c in chunks]
        num_chunks = len(chunks)

        # Check if the expected page from the expected case is in the top-6 chunks
        page_ok = False
        for c in chunks:
            if c['case_name'] == expected_case and c['page_number'] in expected_pages:
                page_ok = True
                break

        scores_str = ", ".join(map(str, scores))

        res = {
            "question": question_text,
            "expected_case": expected_case,
            "expected_pages": expected_pages,
            "top_1_case_correct": case_ok,
            "expected_page_in_top_6": page_ok,
            "top_6_relevance_scores": scores,
            "num_retrieved_chunks": num_chunks,
        }

        # ---------------------------
        # 2. Generation (if --full)
        # ---------------------------
        if full_mode:
            retries_count = 0

            def progress_cb(info):
                nonlocal retries_count
                if info.get('retrying'):
                    retries_count += 1

            t0 = time.time()
            if model:
                ans = generate_verified_answer(question_text, chunks, progress_callback=progress_cb, model=model)
            else:
                ans = generate_verified_answer(question_text, chunks, progress_callback=progress_cb)
            t1 = time.time()

            verified = ans.get('verified', False)
            answer_text = ans.get('answer', '')
            gen_time = round(t1 - t0, 2)
            retries = retries_count

            # cites_expected: True only when verified and citations match
            if verified:
                cites_expected = _check_cites_expected(answer_text, expected_case, expected_pages)
            else:
                cites_expected = False

            # Answer length in words (excludes the Sources: line)
            body_lines = [
                line for line in answer_text.splitlines()
                if not line.strip().lower().startswith("sources:")
            ]
            answer_words = len(" ".join(body_lines).split())

            res["verified"] = verified
            res["cites_expected"] = cites_expected
            res["generation_time_seconds"] = gen_time
            res["retries"] = retries
            res["model"] = effective_model
            res["answer_words"] = answer_words

        results.append(res)

        # Print row
        row = f"{i+1:<3} | {str(case_ok):<13} | {str(page_ok):<15} | {scores_str:<35}"
        if full_mode:
            row += (
                f" | {str(verified):<8}"
                f" | {str(cites_expected):<8}"
                f" | {gen_time:<8}"
                f" | {retries:<7}"
                f" | {num_chunks:<6}"
                f" | {answer_words:<7}"
            )
        print(row)

    # ---------------------------
    # Summary
    # ---------------------------
    print("\n--- Summary ---")
    if not results:
        print("No questions evaluated.")
        return

    case_acc = sum(1 for r in results if r['top_1_case_correct']) / len(results) * 100
    page_acc = sum(1 for r in results if r['expected_page_in_top_6']) / len(results) * 100
    print(f"Top-1 Case Accuracy: {case_acc:.1f}%")
    print(f"Top-6 Page Accuracy: {page_acc:.1f}%")

    if full_mode:
        verified_acc = sum(1 for r in results if r['verified']) / len(results) * 100
        cites_acc = sum(1 for r in results if r.get('cites_expected', False)) / len(results) * 100
        mean_chunks = sum(r.get('num_retrieved_chunks', 0) for r in results) / len(results)
        mean_words = sum(r.get('answer_words', 0) for r in results) / len(results)
        print(f"Verified Accuracy:   {verified_acc:.1f}%")
        print(f"Cites Expected:      {cites_acc:.1f}%")
        print(f"Mean chunks retrieved: {mean_chunks:.1f}")
        print(f"Mean answer words:   {mean_words:.1f}")

    # ---------------------------
    # Save Results
    # ---------------------------
    os.makedirs("eval_results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = os.path.join("eval_results", f"{timestamp}.json")

    # Top-level envelope carries the metadata needed for comparison table
    # filtering; per-question detail lives in "results".
    envelope = {
        "eval_questions_hash": questions_hash,
        "run_group": group,
        "model": effective_model,
        "timestamp": timestamp,
        "results": results,
    }

    with open(out_file, 'w') as f:
        json.dump(envelope, f, indent=2)
    print(f"\nResults written to {out_file}")

    if full_mode:
        print("\n--- Model Comparison (Matching Run Group) ---")
        import glob

        # Hash of the current eval_questions.json — only compare runs that
        # used exactly the same question set.
        current_hash = questions_hash
        current_group = group

        model_stats = {}
        for fpath in sorted(glob.glob("eval_results/*.json")):
            with open(fpath, 'r') as f:
                try:
                    envelope_data = json.load(f)
                except json.JSONDecodeError:
                    continue

            # Skip files that are missing the new metadata fields (old format)
            if not isinstance(envelope_data, dict):
                continue
            file_hash = envelope_data.get("eval_questions_hash")
            file_group = envelope_data.get("run_group")
            if file_hash != current_hash or file_group != current_group:
                continue

            run_data = envelope_data.get("results", [])
            if not run_data:
                continue

            m_name = envelope_data.get("model", "unknown")
            if m_name not in model_stats:
                model_stats[m_name] = []
            model_stats[m_name].append(run_data)

        col_w = 25
        print(
            f"{'Model':<{col_w}} | {'n':>4} | {'Verified':>9} | {'Cites OK':>9}"
            f" | {'Mean Time':>10} | {'Mean Retries':>13}"
            f" | {'Mean Chunks':>12} | {'Mean Ans Wds':>13}"
        )
        divider = "-" * (col_w + 4 + 11 + 11 + 12 + 15 + 14 + 15)
        print(divider)

        for m_name, runs in model_stats.items():
            total_qs = 0
            total_verified = 0
            total_cites = 0
            total_time = 0.0
            total_retries = 0
            total_chunks = 0
            total_words = 0
            for run_data in runs:
                total_qs += len(run_data)
                total_verified += sum(1 for r in run_data if r.get("verified", False))
                total_cites += sum(1 for r in run_data if r.get("cites_expected", False))
                total_time += sum(r.get("generation_time_seconds", 0) for r in run_data)
                total_retries += sum(r.get("retries", 0) for r in run_data)
                total_chunks += sum(r.get("num_retrieved_chunks", 0) for r in run_data)
                total_words += sum(r.get("answer_words", 0) for r in run_data)

            if total_qs > 0:
                verified_rate = (total_verified / total_qs) * 100
                cites_rate = (total_cites / total_qs) * 100
                mean_time = total_time / total_qs
                mean_retries = total_retries / total_qs
                mean_chunks = total_chunks / total_qs
                mean_words = total_words / total_qs
                print(
                    f"{m_name:<{col_w}} | {total_qs:>4} | {verified_rate:>8.1f}%"
                    f" | {cites_rate:>8.1f}% | {mean_time:>10.2f}"
                    f" | {mean_retries:>13.2f} | {mean_chunks:>12.1f}"
                    f" | {mean_words:>13.1f}"
                )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Evaluate retrieval and generation pipeline.")
    parser.add_argument('--full', action='store_true', help='Run generation and verification step')
    parser.add_argument('--model', type=str, help='Override model for generation and verification')
    parser.add_argument(
        '--group', type=str, default=None,
        help='Run-group label for comparison table (default: today\'s date YYYY-MM-DD)',
    )
    args = parser.parse_args()

    run_eval(full_mode=args.full, model=args.model, group=args.group)
