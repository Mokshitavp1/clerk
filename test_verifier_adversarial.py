"""
T6 — Adversarial verifier stress test.

This is the highest-priority test in the whole plan: it's the direct check
against your verifier confidently passing a wrong answer, which is the
failure mode that matters most for a tool lawyers will rely on.

All cases here are built from fixtures.CHUNKS_SMITH, so the "correct"
grounded facts are fixed and known:
    - breach of the implied covenant of good faith, by delaying performance
    - $42,000 in damages, for lost profits during the delay

Run:
    pytest tests/test_verifier_adversarial.py -v

Requires `ollama serve` running locally with qwen2.5:7b-instruct pulled —
this calls the real model, it is not mocked, because the whole point is to
test the verifier's actual judgment, not a stub of it.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from verifier import verify_answer
from fixtures import CHUNKS_SMITH, SUPPORTED_ANSWER_TEXT


pytestmark = pytest.mark.requires_ollama


# ---------------------------------------------------------------------------
# (a) Correct facts, wrong citation (right claim, points at the wrong page)
# ---------------------------------------------------------------------------

WRONG_PAGE_CITATION = (
    "The court found the defendant breached the implied covenant of good faith by "
    "delaying performance, and awarded $42,000 in damages for the plaintiff's lost "
    "profits.\n\n"
    "Sources: Smith_v_Jones_2019, p. 12; Smith_v_Jones_2019, p. 19"
)

# ---------------------------------------------------------------------------
# (b) Real citation, misstated holding (cites the right page, wrong claim)
# ---------------------------------------------------------------------------

MISSTATED_HOLDING = (
    "The court found the defendant acted in good faith and was not liable for "
    "any delay, dismissing the plaintiff's claims entirely.\n\n"
    "Sources: Smith_v_Jones_2019, p. 4"
)

# ---------------------------------------------------------------------------
# (c) Fabricated dollar figure not present in any chunk
# ---------------------------------------------------------------------------

FABRICATED_DAMAGES = (
    "The court found the defendant breached the implied covenant of good faith by "
    "delaying performance, and awarded $500,000 in punitive damages for the "
    "plaintiff's lost profits.\n\n"
    "Sources: Smith_v_Jones_2019, p. 4; Smith_v_Jones_2019, p. 7"
)

# ---------------------------------------------------------------------------
# (d) Plausible legal reasoning, zero grounding in the provided chunks
# ---------------------------------------------------------------------------

UNGROUNDED_REASONING = (
    "Under the doctrine of promissory estoppel, the court held that the "
    "defendant's prior assurances to the plaintiff created a binding obligation "
    "independent of the written contract, entitling the plaintiff to specific "
    "performance.\n\n"
    "Sources: Smith_v_Jones_2019, p. 4"
)


ADVERSARIAL_CASES = [
    pytest.param(WRONG_PAGE_CITATION, id="wrong_page_citation"),
    pytest.param(MISSTATED_HOLDING, id="misstated_holding"),
    pytest.param(FABRICATED_DAMAGES, id="fabricated_damages"),
    pytest.param(UNGROUNDED_REASONING, id="ungrounded_reasoning"),
]


class TestAdversarialRejection:
    """Every one of these MUST come back verified=False. A single pass here
    is a false-negative in the safety-critical direction — the verifier let
    something wrong through."""

    @pytest.mark.parametrize("answer_text", ADVERSARIAL_CASES)
    def test_verifier_rejects_adversarial_answer(self, answer_text):
        result = verify_answer(answer_text, CHUNKS_SMITH)
        assert result["verified"] is False, (
            f"Verifier incorrectly passed an adversarial answer as grounded:\n{answer_text}"
        )
        assert result["issue"], "A rejected answer must always carry an issue description."

    def test_all_adversarial_cases_rejected_rate(self):
        """Aggregate check: run the full adversarial set and report the
        rejection rate, so a single flaky pass doesn't hide in a sea of
        green parametrized test names."""
        results = [verify_answer(case.values[0], CHUNKS_SMITH) for case in ADVERSARIAL_CASES]
        rejected = sum(1 for r in results if r["verified"] is False)
        total = len(results)
        assert rejected == total, (
            f"Only {rejected}/{total} adversarial answers were correctly rejected."
        )


class TestFalsePositiveRejectionRate:
    """The opposite failure mode: rejecting answers that ARE correct.
    Over-rejection makes the product unusable even though it's 'safe'.
    Run the known-good answer several times (LLM output isn't fully
    deterministic) and track how often it's wrongly rejected."""

    REPEATS = 5

    def test_supported_answer_rejection_rate(self):
        results = [verify_answer(SUPPORTED_ANSWER_TEXT, CHUNKS_SMITH) for _ in range(self.REPEATS)]
        false_rejections = sum(1 for r in results if r["verified"] is False)
        # Flag rather than hard-fail on the first flake — but any non-zero
        # rate here is worth investigating before you ship this.
        if false_rejections > 0:
            pytest.fail(
                f"{false_rejections}/{self.REPEATS} runs wrongly rejected a fully "
                f"grounded, correct answer. Issues seen: "
                f"{[r['issue'] for r in results if not r['verified']]}"
            )
