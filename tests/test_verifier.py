"""
T3 — Verifier parsing + pass/fail behavior.

Run:
    pytest tests/test_verifier.py -v

The parsing tests (TestParseVerificationResponse) run instantly, no Ollama
required. The end-to-end tests (TestVerifyAnswerEndToEnd) call the real
local model via verifier.verify_answer, so they need `ollama serve` running
and `qwen2.5:7b-instruct` pulled (per CONTRACTS.md) — they're slower and
are marked so you can skip them during quick iteration:

    pytest tests/test_verifier.py -v -m "not requires_ollama"
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from verifier import _parse_verification_response, verify_answer
from fixtures import (
    SUPPORTED_ANSWER_TEXT,
    UNSUPPORTED_ANSWER_TEXT,
    CHUNKS_SMITH,
)


# ---------------------------------------------------------------------------
# _parse_verification_response — pure function, no Ollama needed
# ---------------------------------------------------------------------------

class TestParseVerificationResponse:

    def test_well_formed_yes(self):
        response = "VERIFIED: yes\nISSUE: NONE"
        result = _parse_verification_response(response)
        assert result == {"verified": True, "issue": None}

    def test_well_formed_no_with_issue(self):
        response = (
            "VERIFIED: no\n"
            "ISSUE: The cited page number does not match the excerpt."
        )
        result = _parse_verification_response(response)
        assert result["verified"] is False
        assert result["issue"] == "The cited page number does not match the excerpt."

    def test_case_insensitive_labels(self):
        response = "Verified: YES\nIssue: none"
        result = _parse_verification_response(response)
        assert result["verified"] is True
        assert result["issue"] is None

    def test_true_false_synonyms(self):
        assert _parse_verification_response("VERIFIED: true\nISSUE: NONE")["verified"] is True
        result = _parse_verification_response("VERIFIED: false\nISSUE: bad citation")
        assert result["verified"] is False
        assert result["issue"] == "bad citation"

    def test_no_with_missing_issue_gets_default_message(self):
        response = "VERIFIED: no"
        result = _parse_verification_response(response)
        assert result["verified"] is False
        assert result["issue"] == (
            "The verification model flagged an issue but gave no description."
        )

    def test_contradictory_yes_with_issue_defaults_to_not_verified(self):
        # VERIFIED: yes but ISSUE is filled in anyway -> treat as unsafe/not verified.
        response = "VERIFIED: yes\nISSUE: Actually the damages figure is wrong."
        result = _parse_verification_response(response)
        assert result["verified"] is False
        assert result["issue"] == "Actually the damages figure is wrong."

    def test_unparseable_response_defaults_to_not_verified(self):
        response = "The answer looks fine to me, no complaints."
        result = _parse_verification_response(response)
        assert result["verified"] is False
        assert result["issue"] == "Could not parse the verification model's response."

    def test_empty_response_defaults_to_not_verified(self):
        result = _parse_verification_response("")
        assert result["verified"] is False

    def test_extra_whitespace_and_blank_lines_still_parse(self):
        response = "\n\n  VERIFIED:   yes  \n\n   ISSUE:   NONE   \n"
        result = _parse_verification_response(response)
        assert result == {"verified": True, "issue": None}


# ---------------------------------------------------------------------------
# _check_citations_deterministic — pure function, no Ollama needed
# ---------------------------------------------------------------------------

from verifier import _check_citations_deterministic

class TestDeterministicCitationCheck:
    def setup_method(self):
        self.chunks = [
            {"case_name": "Smith_v_Jones_2019", "page_number": 4, "text": "dummy"},
            {"case_name": "Smith_v_Jones_2019", "page_number": 7, "text": "dummy"},
            {"case_name": "State_v_Doe,Inc._2020", "page_number": 2, "text": "comma in name"}
        ]

    def test_clean_match(self):
        answer = "Some text.\n\nSources: Smith_v_Jones_2019, p. 4; Smith_v_Jones_2019, p. 7"
        res = _check_citations_deterministic(answer, self.chunks)
        assert res["verified"] is True

    def test_rejects_citation_to_case_discussed_but_not_provided(self):
        # The exact Howe v. Smith vulnerability
        answer = "Some text.\n\nSources: Howe v. Smith [1884] Ch. 89"
        res = _check_citations_deterministic(answer, self.chunks)
        assert res["verified"] is False
        assert "no page number found" in res["issue"]

    def test_rejects_off_by_one_page_number(self):
        # Case exists, but page 3 is not in our chunks (we have 4 and 7)
        answer = "Some text.\n\nSources: Smith_v_Jones_2019, p. 3"
        res = _check_citations_deterministic(answer, self.chunks)
        assert res["verified"] is False
        assert "no provided excerpt has this exact (case_name, page_number) pair" in res["issue"]

    def test_handles_comma_in_case_name(self):
        # The parser splits on ';' so a ',' inside a case name shouldn't break it
        answer = "Some text.\n\nSources: State_v_Doe,Inc._2020, p. 2"
        res = _check_citations_deterministic(answer, self.chunks)
        assert res["verified"] is True

    def test_handles_page_number_format_drift(self):
        # LLM might use pg. or Page or p.
        answer = "Some text.\n\nSources: Smith_v_Jones_2019, Pg. 4; Smith_v_Jones_2019, page 7"
        res = _check_citations_deterministic(answer, self.chunks)
        assert res["verified"] is True

    def test_rejects_malformed_page_number(self):
        # Fails closed if the number format drifts too far to parse confidently
        answer = "Some text.\n\nSources: Smith_v_Jones_2019, at paragraph 4"
        res = _check_citations_deterministic(answer, self.chunks)
        assert res["verified"] is False
        assert "no page number found" in res["issue"]

    def test_multiple_citations_to_same_case(self):
        # Tests that splitting by ';' correctly treats each as a separate tuple
        answer = "Some text.\n\nSources: Smith_v_Jones_2019, p. 4; Smith_v_Jones_2019, p. 7"
        res = _check_citations_deterministic(answer, self.chunks)
        assert res["verified"] is True


# ---------------------------------------------------------------------------
# verify_answer — end-to-end, calls the real local model
# ---------------------------------------------------------------------------

requires_ollama = pytest.mark.requires_ollama


@requires_ollama
class TestVerifyAnswerEndToEnd:

    def test_supported_answer_passes(self):
        result = verify_answer(SUPPORTED_ANSWER_TEXT, CHUNKS_SMITH)
        assert result["verified"] is True
        assert result["issue"] is None

    def test_unsupported_answer_fails(self):
        result = verify_answer(UNSUPPORTED_ANSWER_TEXT, CHUNKS_SMITH)
        assert result["verified"] is False
        assert result["issue"] is not None

    def test_returns_contract_3_4_shape(self):
        # CONTRACTS.md 3.4 — exactly these two keys, nothing extra.
        result = verify_answer(SUPPORTED_ANSWER_TEXT, CHUNKS_SMITH)
        assert set(result.keys()) == {"verified", "issue"}
        assert isinstance(result["verified"], bool)
