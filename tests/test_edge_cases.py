"""
T8 — No relevant case in the knowledge base.

Tests the insufficient_cases path at the self_rag layer, which is what
app.py's _run_query checks before ever calling generate/verify. This is
the layer that actually decides "should we even attempt an answer" —
the exact place a fabrication would need to be prevented.

Note: app.py itself runs Streamlit calls at import time (st.set_page_config,
file_uploader, etc.), so it can't be imported directly in a plain unit test
without mocking Streamlit's entire API surface. If you want to verify the
literal UI message shown to the user, use Streamlit's own AppTest framework
(streamlit.testing.v1.AppTest.from_file("app.py")) instead — that's the
tool built for exactly this, rather than hand-rolling Streamlit mocks here.

Run:
    pytest tests/test_edge_cases.py -v
"""

import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from self_rag import get_graded_cases


class TestNoRelevantCaseInKB:

    @patch("self_rag.get_relevant_chunks")
    @patch("self_rag.get_relevant_cases")
    def test_empty_kb_yields_insufficient(self, mock_stage1, mock_stage2):
        # KB has nothing at all -- Stage 1 returns no shortlist.
        mock_stage1.return_value = []
        mock_stage2.return_value = []

        result = get_graded_cases("what is the standard for X?", min_cases_required=2)

        assert result["insufficient_cases"] is True
        assert result["cases"] == []

    @patch("self_rag.get_relevant_chunks")
    @patch("self_rag.get_relevant_cases")
    def test_shortlisted_but_nothing_survives_grading(self, mock_stage1, mock_stage2):
        # KB has cases, Stage 1 shortlists some, but nothing is actually
        # relevant enough to survive the relevance floor in grading.
        mock_stage1.return_value = [
            {"case_name": "Unrelated_Case_2020", "relevance_score": 0.15},
            {"case_name": "Another_Unrelated_2018", "relevance_score": 0.11},
        ]
        mock_stage2.return_value = []  # nothing retrieved for either case

        result = get_graded_cases("completely off-topic query", min_cases_required=2)

        assert result["insufficient_cases"] is True
        assert result["cases"] == []

    @patch("self_rag.get_relevant_chunks")
    @patch("self_rag.get_relevant_cases")
    def test_never_fabricates_a_case_when_none_qualify(self, mock_stage1, mock_stage2):
        # Explicit non-fabrication check: even if Stage 1 returns candidates,
        # if none survive grading, "cases" must be empty -- never populated
        # with a low-confidence guess dressed up as a real result.
        mock_stage1.return_value = [{"case_name": "Weak_Match_2021", "relevance_score": 0.22}]
        mock_stage2.return_value = [
            {
                "text": "Barely related text.",
                "case_name": "Weak_Match_2021",
                "page_number": 1,
                "relevance_score": 0.1,  # below the 0.4 grading floor
            }
        ]

        result = get_graded_cases("query", min_cases_required=1)

        assert result["cases"] == []
        assert result["insufficient_cases"] is True
