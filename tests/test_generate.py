"""
T4 — Tag-based citation machinery in generate.py.

Tests cover the two pure functions (_assign_tags, _expand_tagged_sources)
that form the tag round-trip: chunks-in → short tags in the prompt →
model echoes tags → real citations restored before anything else sees them.

All tests here are deterministic (no Ollama). Run with:
    pytest tests/test_generate.py -v

Or as part of the full fast suite:
    pytest -v -m "not requires_ollama"
"""

import pytest

from generate import _assign_tags, _expand_tagged_sources, build_answer_prompt


# ---------------------------------------------------------------------------
# _assign_tags
# ---------------------------------------------------------------------------

class TestAssignTags:

    def test_positional_and_unique(self):
        chunks = [
            {"text": "a", "case_name": "Case_A", "page_number": 1},
            {"text": "b", "case_name": "Case_B", "page_number": 6},
        ]
        tag_map, tagged = _assign_tags(chunks)
        assert tag_map == {
            "C1": {"case_name": "Case_A", "page_number": 1},
            "C2": {"case_name": "Case_B", "page_number": 6},
        }
        assert [tag for tag, _ in tagged] == ["C1", "C2"]

    def test_chunks_paired_in_output(self):
        """Each (tag, chunk) pair in tagged_chunks references the original chunk."""
        chunks = [
            {"text": "alpha", "case_name": "X", "page_number": 3},
        ]
        tag_map, tagged = _assign_tags(chunks)
        assert len(tagged) == 1
        tag, chunk = tagged[0]
        assert tag == "C1"
        assert chunk is chunks[0]

    def test_single_chunk(self):
        chunks = [{"text": "x", "case_name": "Only_Case", "page_number": 99}]
        tag_map, tagged = _assign_tags(chunks)
        assert list(tag_map.keys()) == ["C1"]
        assert tag_map["C1"]["page_number"] == 99

    def test_empty_chunks(self):
        tag_map, tagged = _assign_tags([])
        assert tag_map == {}
        assert tagged == []

    def test_ignores_extra_keys(self):
        """Chunks may carry relevance_score and other keys — tag_map should only
        keep case_name and page_number, per CONTRACTS.md 3.2."""
        chunks = [{"text": "t", "case_name": "A", "page_number": 2, "relevance_score": 0.9}]
        tag_map, _ = _assign_tags(chunks)
        assert tag_map["C1"] == {"case_name": "A", "page_number": 2}
        assert "relevance_score" not in tag_map["C1"]


class TestAnswerPrompt:

    def test_prompt_requires_rule_and_analogy_analysis(self):
        chunks = [{
            "text": "Section 74 permits reasonable compensation where loss is not proved.",
            "case_name": "Example_Case",
            "page_number": 3,
        }]

        prompt, _ = build_answer_prompt(
            "Is forfeiture valid without proof of government loss, and is there a similar case?",
            chunks,
        )

        assert "Answer the user's actual question first" in prompt
        assert "similar or analogous case" in prompt
        assert "proof of loss" in prompt
        assert "full" in prompt and "reasonable compensation" in prompt
        assert "Separate a court's holding or stated legal rule" in prompt


# ---------------------------------------------------------------------------
# _expand_tagged_sources
# ---------------------------------------------------------------------------

class TestExpandTaggedSources:

    def test_normal_single_tag(self):
        tag_map = {"C1": {"case_name": "Case_A", "page_number": 1}}
        answer = "Some answer text.\n\nSources: C1"
        expanded = _expand_tagged_sources(answer, tag_map)
        assert expanded.endswith("Sources: Case_A, p. 1")

    def test_multiple_tags_semicolon_separated(self):
        tag_map = {
            "C1": {"case_name": "Case_A", "page_number": 1},
            "C2": {"case_name": "Case_B", "page_number": 6},
        }
        answer = "Answer body.\n\nSources: C1, C2"
        expanded = _expand_tagged_sources(answer, tag_map)
        assert "Case_A, p. 1" in expanded
        assert "Case_B, p. 6" in expanded

    def test_hallucinated_tag_flagged_not_dropped(self):
        """A tag the model invented (not in tag_map) must produce an
        [unresolved citation: Cx] marker — silent drops are banned because
        they'd let a missing-attribution claim pass the citation check."""
        tag_map = {"C1": {"case_name": "Case_A", "page_number": 1}}
        answer = "Some answer text.\n\nSources: C1, C7"
        expanded = _expand_tagged_sources(answer, tag_map)
        assert "Case_A, p. 1" in expanded
        assert "[unresolved citation: C7]" in expanded

    def test_missing_sources_line_passthrough(self):
        """No Sources line → return unchanged so verify_answer can catch it."""
        answer = "Some answer text with no sources line."
        result = _expand_tagged_sources(answer, {"C1": {"case_name": "X", "page_number": 1}})
        assert result == answer

    def test_body_text_preserved(self):
        """Everything before the Sources line must be left untouched."""
        tag_map = {"C1": {"case_name": "Case_A", "page_number": 2}}
        body = "The court held that X.\n\nFurthermore, Y applies."
        answer = body + "\n\nSources: C1"
        expanded = _expand_tagged_sources(answer, tag_map)
        assert expanded.startswith(body)

    def test_case_name_with_underscores_preserved_exactly(self):
        """The exact case_name string — including underscores and date suffix —
        must survive the round-trip without alteration."""
        name = "Oil_Natural_Gas_Corporation_Ltd_vs_Saw_Pipes_Ltd_on_17_April_2003"
        tag_map = {"C1": {"case_name": name, "page_number": 33}}
        answer = "Answer.\n\nSources: C1"
        expanded = _expand_tagged_sources(answer, tag_map)
        assert name in expanded

    def test_sources_line_case_insensitive_match(self):
        """The Sources line regex should find the line regardless of leading
        whitespace or capitalisation variance."""
        tag_map = {"C1": {"case_name": "Case_A", "page_number": 1}}
        answer = "Body text.\n\n  Sources: C1"
        expanded = _expand_tagged_sources(answer, tag_map)
        assert "Case_A, p. 1" in expanded

    def test_empty_tag_map_hallucinated_all(self):
        """If tag_map is empty every tag is unresolved — nothing should crash."""
        answer = "Answer.\n\nSources: C1"
        expanded = _expand_tagged_sources(answer, {})
        assert "[unresolved citation: C1]" in expanded

    def test_inline_body_tag_expanded(self):
        """Inline [Cx] references in the body must be expanded to real names
        so the verifier doesn't see unresolved tags when checking attribution."""
        tag_map = {
            "C1": {"case_name": "Case_A", "page_number": 1},
            "C2": {"case_name": "Case_B", "page_number": 6},
        }
        answer = "[C1] held X. [C2] also held Y.\n\nSources: C1, C2"
        expanded = _expand_tagged_sources(answer, tag_map)
        assert "[Case_A, p. 1]" in expanded
        assert "[Case_B, p. 6]" in expanded
        # Sources line is still fully expanded
        assert "Sources: Case_A, p. 1; Case_B, p. 6" in expanded

    def test_inline_hallucinated_tag_flagged(self):
        """An inline tag not in tag_map must become [unresolved citation: Cx],
        not be silently dropped or left as a raw bracket label."""
        tag_map = {"C1": {"case_name": "Case_A", "page_number": 1}}
        answer = "[C1] held X. [C9] also held Y.\n\nSources: C1"
        expanded = _expand_tagged_sources(answer, tag_map)
        assert "[unresolved citation: C9]" in expanded
        assert "[Case_A, p. 1]" in expanded
