"""
T1 — Stage 1 shape + routing logic.

Pure functions, no Ollama/ChromaDB needed — runs instantly.

Run:
    pytest tests/test_router.py -v
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from router import decide_mode, build_confidence_line, build_warning
from fixtures import STAGE1_CLEAR, STAGE1_AMBIGUOUS


class TestDecideMode:

    def test_clear_dominant_case_returns_fast(self):
        assert decide_mode(STAGE1_CLEAR) == "fast"

    def test_ambiguous_top_two_returns_deep(self):
        assert decide_mode(STAGE1_AMBIGUOUS) == "deep"

    def test_single_result_returns_fast(self):
        assert decide_mode([{"case_name": "Only_Case", "relevance_score": 0.5}]) == "fast"

    def test_empty_results_returns_fast(self):
        assert decide_mode([]) == "fast"

    def test_boundary_exactly_at_threshold_is_ambiguous(self):
        # top - second == threshold (0.1) -> "<=" means this counts as ambiguous
        results = [
            {"case_name": "A", "relevance_score": 0.60},
            {"case_name": "B", "relevance_score": 0.50},
        ]
        assert decide_mode(results, threshold=0.1) == "deep"

    def test_just_above_threshold_is_fast(self):
        results = [
            {"case_name": "A", "relevance_score": 0.601},
            {"case_name": "B", "relevance_score": 0.50},
        ]
        assert decide_mode(results, threshold=0.1) == "fast"


class TestBuildConfidenceLine:

    def test_names_top_case(self):
        line = build_confidence_line(STAGE1_CLEAR)
        assert "Smith_v_Jones_2019" in line

    def test_empty_results_says_no_match(self):
        line = build_confidence_line([])
        assert "No matching case" in line

    def test_shown_regardless_of_ambiguity(self):
        # build_confidence_line is not itself a judgment about confidence -
        # it should still name the top case even when ambiguous.
        line = build_confidence_line(STAGE1_AMBIGUOUS)
        assert "Smith_v_Jones_2019" in line


class TestBuildWarning:

    def test_clear_case_returns_none(self):
        assert build_warning(STAGE1_CLEAR) is None

    def test_ambiguous_case_returns_contract_3_5_shape(self):
        warning = build_warning(STAGE1_AMBIGUOUS)
        assert warning is not None
        assert set(warning.keys()) == {"message", "explain_why"}
        assert isinstance(warning["message"], str) and warning["message"]
        assert isinstance(warning["explain_why"], str) and warning["explain_why"]

    def test_warning_names_both_competing_cases(self):
        warning = build_warning(STAGE1_AMBIGUOUS)
        assert "Smith_v_Jones_2019" in warning["explain_why"]
        assert "Doe_v_Acme_Corp_2021" in warning["explain_why"]

    def test_single_result_returns_none(self):
        assert build_warning([{"case_name": "Only_Case", "relevance_score": 0.5}]) is None

    def test_empty_results_returns_none(self):
        assert build_warning([]) is None
