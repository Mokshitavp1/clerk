"""
T12 — Bulk ingestion load test.

Ingests a folder of real case PDFs sequentially through ingest.py, logging
per-document time and process memory, to characterize how ingestion scales
on your actual demo/sale machine. Also includes a kill-mid-ingest check for
the non-atomic replace_case behavior noted in CONTRACTS.md.

SETUP:
    Download 200-500 real case PDFs into a folder, e.g. from:
      - CourtListener: https://www.courtlistener.com/
      - CourtListener bulk data: https://wiki.free.law/c/courtlistener/help/api/bulk-data/bulk-legal-data
      - Caselaw Access Project on HF: https://huggingface.co/datasets/free-law/Caselaw_Access_Project

USAGE:
    python scripts/load_test_ingest.py --pdf-dir path/to/pdfs --limit 200

Requires a real local Ollama + embedding model, since this calls the real
ingest.py pipeline -- there is no meaningful way to fake this with fixtures.
"""

import argparse
import os
import sys
import time
import glob
import csv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import psutil
except ImportError:
    psutil = None


def _current_memory_mb():
    if psutil is None:
        return None
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)


def run_load_test(pdf_dir, limit, log_path):
    from ingest import ingest_new_case

    pdf_paths = sorted(glob.glob(os.path.join(pdf_dir, "*.pdf")))[:limit]
    if not pdf_paths:
        print(f"No PDFs found in {pdf_dir}")
        sys.exit(1)

    print(f"Ingesting {len(pdf_paths)} PDFs from {pdf_dir}...")
    if psutil is None:
        print("(psutil not installed -- memory tracking disabled. "
              "pip install psutil --break-system-packages for memory stats.)")

    results = []
    overall_start = time.time()

    for i, pdf_path in enumerate(pdf_paths):
        file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
        mem_before = _current_memory_mb()
        start = time.time()
        error = None

        try:
            case_name = ingest_new_case(pdf_path)
        except Exception as e:
            case_name = None
            error = str(e)

        elapsed = time.time() - start
        mem_after = _current_memory_mb()

        results.append({
            "index": i,
            "file": os.path.basename(pdf_path),
            "file_size_mb": round(file_size_mb, 2),
            "elapsed_seconds": round(elapsed, 2),
            "mem_before_mb": round(mem_before, 1) if mem_before else "",
            "mem_after_mb": round(mem_after, 1) if mem_after else "",
            "case_name": case_name,
            "error": error or "",
        })

        status = "OK" if error is None else f"FAILED: {error}"
        print(f"  [{i + 1}/{len(pdf_paths)}] {os.path.basename(pdf_path)} "
              f"({file_size_mb:.1f}MB) -> {elapsed:.2f}s -- {status}")

    total_elapsed = time.time() - overall_start
    failures = [r for r in results if r["error"]]

    with open(log_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"\n--- Summary ---")
    print(f"Total: {len(results)} PDFs in {total_elapsed:.1f}s "
          f"({total_elapsed / max(len(results), 1):.2f}s/doc average)")
    print(f"Failures: {len(failures)}/{len(results)}")
    if failures:
        print("Failed files:")
        for f_result in failures:
            print(f"  - {f_result['file']}: {f_result['error']}")
    print(f"Detailed log written to {log_path}")


def kill_mid_ingest_check(pdf_path):
    """
    Manual check for replace_case's non-atomic delete-then-reingest behavior.
    This can't be automated cleanly (it needs an actual process kill), so
    this prints instructions rather than doing it programmatically.
    """
    print(
        "\nTo test replace_case's non-atomic failure mode manually:\n"
        "  1. Run: python -c \"import sys; sys.path.insert(0, 'ingestion'); "
        f"from ingest import replace_case; replace_case(r'{pdf_path}')\"\n"
        "  2. While it's running, kill the process (Ctrl+C or Task Manager) "
        "partway through -- ideally between the delete and re-ingest steps.\n"
        "  3. Check data/chroma_db/ afterward: is the case now MISSING entirely "
        "(acceptable-but-degraded) or does the KB report inconsistent state?\n"
        "  4. Document whatever you find -- this determines whether a rebuild "
        "interrupted mid-way needs a documented recovery step before sale."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf-dir", required=True, help="Folder of PDFs to ingest")
    parser.add_argument("--limit", type=int, default=200, help="Max number of PDFs to ingest")
    parser.add_argument("--log", default="load_test_results.csv", help="Output CSV path")
    parser.add_argument("--kill-check-instructions", action="store_true",
                         help="Print manual instructions for the non-atomic replace_case check")
    args = parser.parse_args()

    if args.kill_check_instructions:
        sample = sorted(glob.glob(os.path.join(args.pdf_dir, "*.pdf")))
        kill_mid_ingest_check(sample[0] if sample else "<path_to_a_pdf>")
    else:
        run_load_test(args.pdf_dir, args.limit, args.log)
