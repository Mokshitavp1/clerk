"""
T10 — Long-document summarization truncation (known limitation).

TestTruncationMechanics tests build_summary_prompt's truncation behavior
directly -- pure string logic, no Ollama needed, runs immediately.

TestHoldingSurvivesTruncation is the real question this whole test exists
to answer: does the truncation cut off before the holding is stated? That
requires an actual model call to summarize the truncated text and a real
long case to test against.

Run:
    pytest tests/test_summarizer_truncation.py -v -m "not requires_ollama"
    pytest tests/test_summarizer_truncation.py -v   # full, needs Ollama + a real long case
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from summarizer import build_summary_prompt, summarize_case, WORD_LIMIT


class TestTruncationMechanics:

    def test_short_text_is_not_truncated(self):
        short_text = "This is a short case summary. " * 10  # well under WORD_LIMIT
        prompt = build_summary_prompt(short_text)
        assert "[TRUNCATED" not in prompt

    def test_long_text_is_truncated_at_word_limit(self):
        long_text = " ".join(f"word{i}" for i in range(WORD_LIMIT + 500))
        prompt = build_summary_prompt(long_text)
        assert "[TRUNCATED: document exceeded 6000 words" in prompt

    def test_truncation_keeps_exactly_word_limit_words_of_original_text(self):
        long_text = " ".join(f"tok{i}" for i in range(WORD_LIMIT + 500))
        prompt = build_summary_prompt(long_text)
        # The last token that should survive truncation, and the first one
        # that should NOT -- exact boundary check instead of a fragile
        # substring count (which the prompt's own wording, e.g. "150 words",
        # can pollute).
        assert f"tok{WORD_LIMIT - 1}" in prompt
        assert f"tok{WORD_LIMIT} " not in prompt and not prompt.rstrip().endswith(f"tok{WORD_LIMIT}")

    def test_truncation_cuts_off_content_after_the_limit(self):
        # A holding-like sentence placed at word 6500 (past the 6000-word
        # limit) should NOT appear in the prompt sent to the model --
        # this demonstrates the exact failure mode: a holding stated only
        # near the end of a long opinion gets silently dropped.
        words = [f"word{i}" for i in range(WORD_LIMIT + 1000)]
        words[WORD_LIMIT + 200] = "HOLDING_MARKER_TOKEN"
        long_text = " ".join(words)

        prompt = build_summary_prompt(long_text)
        assert "HOLDING_MARKER_TOKEN" not in prompt

    def test_holding_before_limit_is_preserved(self):
        # Sanity check the inverse: a marker placed well before the limit
        # should survive.
        words = [f"word{i}" for i in range(WORD_LIMIT + 1000)]
        words[100] = "HOLDING_MARKER_TOKEN"
        long_text = " ".join(words)

        prompt = build_summary_prompt(long_text)
        assert "HOLDING_MARKER_TOKEN" in prompt


@pytest.mark.requires_ollama
class TestHoldingSurvivesTruncation:
    """Requires a REAL long case where you know where the holding is stated.
    Fill in LONG_CASE_TEXT and HOLDING_LOCATION below with a real opinion
    from CourtListener before running this -- there's no way to test this
    meaningfully with synthetic text, since it's specifically about whether
    a real model can still produce a usable summary from truncated real
    legal prose."""

    # TODO: replace with a real 8000+ word opinion's full text, and note
    # whether its holding appears in the first 6000 words or after.
    LONG_CASE_TEXT = None
    HOLDING_KEYWORDS = []  # e.g. ["affirmed", "reversed", "$"] specific to your case

    @pytest.mark.skipif(
        True,  # flip to a real check once LONG_CASE_TEXT is filled in
        reason="Fill in LONG_CASE_TEXT and HOLDING_KEYWORDS with a real long opinion first.",
    )
    def test_summary_still_mentions_the_holding(self):
        summary = summarize_case([{"text": self.LONG_CASE_TEXT, "page_number": 1}])
        found = any(keyword.lower() in summary.lower() for keyword in self.HOLDING_KEYWORDS)
        assert found, (
            "Summary of a truncated long document did not mention the holding -- "
            "this confirms the known truncation limitation actually loses "
            "outcome-relevant information, not just stylistic detail."
        )
