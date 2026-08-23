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
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from verifier import _parse_verification_response, verify_answer, _check_has_content
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

    def test_underscore_vs_space_variant_passes(self):
        # The chunks have "Smith_v_Jones_2019"
        # The answer cites "Smith v Jones 2019"
        answer = "Some text.\n\nSources: Smith v Jones 2019, p. 4"
        res = _check_citations_deterministic(answer, self.chunks)
        assert res["verified"] is True

    def test_omitted_date_suffix_passes(self):
        # Create a new chunk with an Indian Kanoon style date suffix
        chunks = self.chunks + [{"case_name": "Fateh_Chand_vs_Balkishan_Das_on_15_January_1963", "page_number": 7, "text": "dummy"}]
        # Cite it without the date suffix and with spaces instead of underscores
        answer = "Some text.\n\nSources: Fateh Chand vs Balkishan Das, p. 7"
        res = _check_citations_deterministic(answer, chunks)
        assert res["verified"] is True

    def test_genuinely_wrong_case_fails(self):
        answer = "Some text.\n\nSources: Smith v Acme, p. 4"
        res = _check_citations_deterministic(answer, self.chunks)
        assert res["verified"] is False
        assert "no provided excerpt has this exact (case_name, page_number) pair" in res["issue"]

    def test_hallucinated_case_sharing_words_fails(self):
        # Shares words with Smith_v_Jones_2019 but is not the same case
        answer = "Some text.\n\nSources: Smith v Doe 2019, p. 4"
        res = _check_citations_deterministic(answer, self.chunks)
        assert res["verified"] is False
        
    def test_multiple_citations_to_same_case(self):
        # Tests that splitting by ';' correctly treats each as a separate tuple
        answer = "Some text.\n\nSources: Smith_v_Jones_2019, p. 4; Smith_v_Jones_2019, p. 7"
        res = _check_citations_deterministic(answer, self.chunks)
        assert res["verified"] is True


# ---------------------------------------------------------------------------
# _check_has_content — pure function, no Ollama needed
# ---------------------------------------------------------------------------

from verifier import _check_has_content, BODY_MIN_WORDS

class TestContentCheck:
    """Tests for the layer-1b deterministic body-content pre-check.

    All cases run instantly without Ollama — _check_has_content is a pure
    function with no external dependencies.
    """

    # Reuse the same chunk set as the citation tests (content doesn't matter
    # for _check_has_content, but we need *something* for the verify_answer
    # integration test below).
    CHUNKS = [
        {"case_name": "Smith_v_Jones_2019", "page_number": 4, "text": "dummy"},
    ]
    VALID_SOURCES = "Sources: Smith_v_Jones_2019, p. 4"

    def test_sources_only_is_rejected(self):
        """An answer that is literally only a Sources: line has no body."""
        answer = "Sources: Smith_v_Jones_2019, p. 4"
        res = _check_has_content(answer)
        assert res["verified"] is False
        assert "no substantive content" in res["issue"]

    def test_sources_only_with_blank_lines_is_rejected(self):
        """Blank lines before the Sources: line do not count as body words."""
        answer = "\n\n\nSources: Smith_v_Jones_2019, p. 4"
        res = _check_has_content(answer)
        assert res["verified"] is False
        assert "no substantive content" in res["issue"]

    def test_body_below_threshold_is_rejected(self):
        """A body with fewer than BODY_MIN_WORDS words must be rejected."""
        # Construct a body that is exactly BODY_MIN_WORDS - 1 words.
        short_body = " ".join(["word"] * (BODY_MIN_WORDS - 1))
        answer = f"{short_body}\n\n{self.VALID_SOURCES}"
        res = _check_has_content(answer)
        assert res["verified"] is False
        assert "no substantive content" in res["issue"]

    def test_body_above_threshold_passes(self):
        """A body with at least BODY_MIN_WORDS words must be accepted."""
        sufficient_body = " ".join(["word"] * BODY_MIN_WORDS)
        answer = f"{sufficient_body}\n\n{self.VALID_SOURCES}"
        res = _check_has_content(answer)
        assert res["verified"] is True
        assert res["issue"] is None

    def test_multi_paragraph_body_counted_correctly(self):
        """Blank lines inside the body should not disrupt word counting."""
        para1 = " ".join(["word"] * 8)
        para2 = " ".join(["word"] * 8)
        # Total 16 words, split across two paragraphs with a blank line between
        answer = f"{para1}\n\n{para2}\n\n{self.VALID_SOURCES}"
        res = _check_has_content(answer)
        assert res["verified"] is True
        assert res["issue"] is None

    def test_verify_answer_short_circuits_without_llm_call(self):
        """verify_answer must not call ollama.chat when the body is empty.

        The content pre-check (layer 1b) runs before the LLM call — if it
        rejects the answer, ollama.chat should never be invoked.
        """
        # A sources-only answer that has a valid citation (passes layer 1)
        # but no prose body (fails layer 1b).
        answer = self.VALID_SOURCES  # no body at all

        with patch("verifier.ollama.chat") as mock_chat:
            result = verify_answer(answer, self.CHUNKS)

        mock_chat.assert_not_called()
        assert result["verified"] is False
        assert "no substantive content" in result["issue"]


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
