import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
for _folder in ("retrieval", "generation", "routing", "ingestion"):
    _path = os.path.join(PROJECT_ROOT, _folder)
    if _path not in sys.path:
        sys.path.insert(0, _path)

from stage1_case_retrieval import get_relevant_cases
from stage2_chunk_retrieval import get_relevant_chunks
from self_rag import get_graded_cases
from verifier import generate_verified_answer_per_case

def dummy_progress(signal):
    if signal.get("retrying"):
        issue = (signal.get("issue") or "")[:120]
        print(f"[PROGRESS] retrying - issue: {issue}")
    elif signal.get("verified"):
        print(f"[PROGRESS] verified")
    else:
        issue = (signal.get("issue") or "")[:120]
        print(f"[PROGRESS] failed - issue: {issue}")

question = "Under what conditions can a seller forfeit earnest money or an advance payment?"

print("Getting relevant cases...")
shortlisted_cases = get_relevant_cases(question)
print(f"Got {len(shortlisted_cases)} cases")

print("Grading cases...")
graded = get_graded_cases(question, progress_callback=lambda s: print(f"Grade progress: {s}"))
if graded["insufficient_cases"]:
    print("Insufficient cases")
else:
    capped_cases = [
        {
            **case,
            "chunks": sorted(
                case["chunks"], key=lambda c: c["relevance_score"], reverse=True
            )[:2],
        }
        for case in graded["cases"]
    ]
    print(f"Sending {len(capped_cases)} cases to generator")
    for case in capped_cases:
        print(f"  - Case {case['case_name']} has {len(case['chunks'])} chunks")
    
    result = generate_verified_answer_per_case(
        question, capped_cases, progress_callback=dummy_progress
    )
    print("RESULT:")
    print(result)
