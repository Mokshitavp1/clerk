"""
Fixture data for Person B to build and test generation/verification/routing code
without needing Person A's ingestion + retrieval pipeline finished or even present.

Shapes here match CONTRACTS.md exactly. If Person A changes a shape, update both
files in the same commit.

Usage example:
    from fixtures import STAGE1_CLEAR, CHUNKS_SMITH
    from routing.router import decide_mode
    print(decide_mode(STAGE1_CLEAR))  # -> "fast"
"""

# --------------------------------------------------------------------------
# Stage 1 results (contract 3.1) — one case clearly dominates
# --------------------------------------------------------------------------
STAGE1_CLEAR = [
    {"case_name": "Smith_v_Jones_2019", "relevance_score": 0.87},
    {"case_name": "Doe_v_Acme_Corp_2021", "relevance_score": 0.41},
    {"case_name": "Roe_v_Statewide_2017", "relevance_score": 0.33},
]

# --------------------------------------------------------------------------
# Stage 1 results — genuinely ambiguous (top two scores within 0.1)
# --------------------------------------------------------------------------
STAGE1_AMBIGUOUS = [
    {"case_name": "Smith_v_Jones_2019", "relevance_score": 0.74},
    {"case_name": "Doe_v_Acme_Corp_2021", "relevance_score": 0.69},
    {"case_name": "Roe_v_Statewide_2017", "relevance_score": 0.35},
]

# --------------------------------------------------------------------------
# Chunks (contract 3.2) — belonging to one case, for a Fast-mode-style test
# --------------------------------------------------------------------------
CHUNKS_SMITH = [
    {
        "text": (
            "The court held that the defendant breached the implied covenant of "
            "good faith by unreasonably delaying performance under the contract."
        ),
        "case_name": "Smith_v_Jones_2019",
        "page_number": 4,
        "relevance_score": 0.81,
    },
    {
        "text": (
            "Damages were awarded in the amount of $42,000, reflecting the "
            "plaintiff's lost profits during the delay period."
        ),
        "case_name": "Smith_v_Jones_2019",
        "page_number": 7,
        "relevance_score": 0.76,
    },
]

# --------------------------------------------------------------------------
# Chunks spanning multiple cases, for a Deep-Thinking-style test
# --------------------------------------------------------------------------
CHUNKS_MULTI_CASE = CHUNKS_SMITH + [
    {
        "text": (
            "The appellate court found that a similar delay, absent bad faith, "
            "did not constitute a breach on its own."
        ),
        "case_name": "Doe_v_Acme_Corp_2021",
        "page_number": 2,
        "relevance_score": 0.69,
    },
]

# --------------------------------------------------------------------------
# Graded cases result (contract 3.3)
# --------------------------------------------------------------------------
GRADED_CASES_OK = {
    "cases": [
        {
            "case_name": "Smith_v_Jones_2019",
            "relevance_score": 0.87,
            "chunks": CHUNKS_SMITH,
        },
        {
            "case_name": "Doe_v_Acme_Corp_2021",
            "relevance_score": 0.69,
            "chunks": [CHUNKS_MULTI_CASE[2]],
        },
    ],
    "insufficient_cases": False,
}

GRADED_CASES_INSUFFICIENT = {
    "cases": [],
    "insufficient_cases": True,
}

# --------------------------------------------------------------------------
# A deliberately unsupported answer, for testing verify_answer's failure path
# --------------------------------------------------------------------------
UNSUPPORTED_ANSWER_TEXT = (
    "The court awarded $500,000 in punitive damages due to fraud.\n\n"
    "Sources: Smith_v_Jones_2019, p. 4"
)

# A grounded answer that should pass verification against CHUNKS_SMITH
SUPPORTED_ANSWER_TEXT = (
    "The court found the defendant breached the implied covenant of good faith by "
    "delaying performance, and awarded $42,000 in damages for the plaintiff's lost "
    "profits.\n\n"
    "Sources: Smith_v_Jones_2019, p. 4; Smith_v_Jones_2019, p. 7"
)
