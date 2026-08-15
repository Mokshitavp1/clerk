"""
T2 — Graded-cases contract shape (CONTRACTS.md 3.3).

Mocks stage1_case_retrieval.get_relevant_cases and
stage2_chunk_retrieval.get_relevant_chunks so this runs with no real
ChromaDB or embedding model needed.

Run:
    pytest tests/test_self_rag.py -v
"""

import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from self_rag import grade_chunks, get_graded_cases
from fixtures import CHUNKS_SMITH, CHUNKS_MULTI_CASE


# ---------------------------------------------------------------------------
# grade_chunks — pure function, no mocking needed
# ---------------------------------------------------------------------------

class TestGradeChunks:

    def test_all_chunks_above_floor_survive(self):
        # CHUNKS_SMITH scores are 0.81 and 0.76, both above default 0.4 floor
        filtered, dropped = grade_chunks(CHUNKS_SMITH)
        assert len(filtered) == 2
        assert dropped == {}

    def test_chunks_below_floor_are_dropped(self):
        low_score_chunk = {**CHUNKS_SMITH[0], "relevance_score": 0.1}
        filtered, dropped = grade_chunks([low_score_chunk], relevance_floor=0.4)
        assert filtered == []
        assert dropped == {"Smith_v_Jones_2019": 1}

    def test_dropped_count_grouped_per_case(self):
        low_a = {**CHUNKS_SMITH[0], "relevance_score": 0.1, "case_name": "A"}
        low_a2 = {**CHUNKS_SMITH[0], "relevance_score": 0.05, "case_name": "A"}
        low_b = {**CHUNKS_SMITH[0], "relevance_score": 0.2, "case_name": "B"}
        filtered, dropped = grade_chunks([low_a, low_a2, low_b], relevance_floor=0.4)
        assert filtered == []
        assert dropped == {"A": 2, "B": 1}

    def test_case_with_zero_drops_absent_from_dict(self):
        filtered, dropped = grade_chunks(CHUNKS_SMITH, relevance_floor=0.4)
        assert "Smith_v_Jones_2019" not in dropped

    def test_original_relative_order_preserved(self):
        filtered, _ = grade_chunks(CHUNKS_MULTI_CASE, relevance_floor=0.4)
        assert [c["case_name"] for c in filtered] == [c["case_name"] for c in CHUNKS_MULTI_CASE]


# ---------------------------------------------------------------------------
# get_graded_cases — full orchestration, Stage 1/2 mocked
# ---------------------------------------------------------------------------

class TestGetGradedCases:

    @patch("self_rag.get_relevant_chunks")
    @patch("self_rag.get_relevant_cases")
    def test_sufficient_cases_returns_contract_3_3_shape(self, mock_stage1, mock_stage2):
        mock_stage1.return_value = [
            {"case_name": "Smith_v_Jones_2019", "relevance_score": 0.87},
            {"case_name": "Doe_v_Acme_Corp_2021", "relevance_score": 0.69},
        ]
        mock_stage2.return_value = CHUNKS_SMITH

        result = get_graded_cases("some query", min_cases_required=2)

        assert set(result.keys()) == {"cases", "insufficient_cases"}
        assert result["insufficient_cases"] is False
        assert len(result["cases"]) == 2
        for case in result["cases"]:
            assert set(case.keys()) == {"case_name", "relevance_score", "chunks"}

    @patch("self_rag.get_relevant_chunks")
    @patch("self_rag.get_relevant_cases")
    def test_insufficient_cases_yields_empty_cases_list(self, mock_stage1, mock_stage2):
        # Every attempt (both the initial try and the retry) returns nothing
        # useful, so this should end in the insufficient_cases=True branch.
        mock_stage1.return_value = [{"case_name": "Lonely_Case_2020", "relevance_score": 0.3}]
        mock_stage2.return_value = []  # no chunks survive -> case doesn't survive grading

        result = get_graded_cases("obscure query", min_cases_required=2)

        assert result["insufficient_cases"] is True
        assert result["cases"] == []

    @patch("self_rag.get_relevant_chunks")
    @patch("self_rag.get_relevant_cases")
    def test_retries_exactly_once_with_doubled_top_k(self, mock_stage1, mock_stage2):
        mock_stage1.return_value = [{"case_name": "Lonely_Case_2020", "relevance_score": 0.3}]
        mock_stage2.return_value = []

        get_graded_cases("query", initial_top_k=5, min_cases_required=2)

        # attempt 1: top_k=5, attempt 2 (retry): top_k=10 -- then stop (no third attempt)
        called_top_ks = [call.kwargs.get("top_k", call.args[1] if len(call.args) > 1 else None)
                          for call in mock_stage1.call_args_list]
        assert mock_stage1.call_count == 2
        assert called_top_ks[0] == 5
        assert called_top_ks[1] == 10

    @patch("self_rag.get_relevant_chunks")
    @patch("self_rag.get_relevant_cases")
    def test_progress_callback_receives_expected_keys(self, mock_stage1, mock_stage2):
        mock_stage1.return_value = [{"case_name": "Smith_v_Jones_2019", "relevance_score": 0.87}]
        mock_stage2.return_value = CHUNKS_SMITH

        received = []
        get_graded_cases("query", min_cases_required=1, progress_callback=received.append)

        assert len(received) >= 1
        for signal in received:
            assert set(signal.keys()) == {
                "attempt", "shortlisted", "surviving", "dropped_chunks", "retrying"
            }
