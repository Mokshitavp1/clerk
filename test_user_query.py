"""One-shot test of the user's actual question from the app."""
import os, sys
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
for _folder in ("retrieval", "generation", "routing", "ingestion"):
    _path = os.path.join(PROJECT_ROOT, _folder)
    if _path not in sys.path:
        sys.path.insert(0, _path)

from run_query_with_timing import run_query_with_timing

run_query_with_timing(
    "What was the High Court decision regarding the amount to be awarded to the plaintiff, and what interest rate was applied?"
)
