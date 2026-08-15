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
