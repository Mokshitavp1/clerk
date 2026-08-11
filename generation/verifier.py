"""
Citation and groundedness verification for generated answers.

verify_answer checks a generated answer against the chunks it was built
from, to catch invented facts or citations that don't actually match the
chunk text they claim to come from.
"""

import ollama

from generate import generate_answer


def _build_verification_prompt(answer_text, chunks):
    """
    Build a prompt asking an LLM to check an answer's citations and
    groundedness against the source chunks it was generated from.

    Args:
        answer_text: the generated answer, including its "Sources:" line.
        chunks: list of {"text", "case_name", "page_number"} dicts that
            were used to generate answer_text.

    Returns:
        str: a complete verification prompt.
    """
    excerpt_blocks = []
    for chunk in chunks:
        label = f"[{chunk['case_name']}, p. {chunk['page_number']}]"
        excerpt_blocks.append(f"{label}\n{chunk['text']}")
    excerpts_text = "\n\n".join(excerpt_blocks)

    prompt = f"""You are a strict legal fact-checker. Your job is to check whether an \
answer is fully grounded in the excerpts it claims to be based on. Check for two \
things:

1. CITATION ACCURACY: every case name and page number cited in the answer's \
"Sources:" line must correspond to one of the excerpts below, and the claim(s) \
attributed to that citation must actually be supported by that excerpt's text.
2. GROUNDEDNESS: every factual claim in the answer (holdings, dollar amounts, \
dates, outcomes, etc.) must be explicitly present in the excerpts below — not \
invented, not assumed, not brought in from outside knowledge.

EXCERPTS:
\"\"\"
{excerpts_text}
\"\"\"

ANSWER TO CHECK:
\"\"\"
{answer_text}
\"\"\"

Respond in EXACTLY this format, with nothing before or after it:

VERIFIED: yes or no
ISSUE: a one- or two-sentence description of what is wrong (which claim or \
citation, and why), or NONE if VERIFIED is yes"""

    return prompt


def _parse_verification_response(response_text):
    """
    Parse the LLM's strict-format verification response into
    {verified: bool, issue: str or None}.

    Defaults to verified=False with a parse-failure issue if the response
    doesn't match the expected format — an unparseable response should
    never be silently treated as a pass.
    """
    verified = False
    issue = "Could not parse the verification model's response."

    verified_line = None
    issue_line = None

    for line in response_text.splitlines():
        stripped = line.strip()
        if stripped.upper().startswith("VERIFIED:"):
            verified_line = stripped.split(":", 1)[1].strip().lower()
        elif stripped.upper().startswith("ISSUE:"):
            issue_line = stripped.split(":", 1)[1].strip()

    if verified_line in ("yes", "true"):
        verified = True
        issue = None
    elif verified_line in ("no", "false"):
        verified = False
        issue = issue_line if issue_line else "The verification model flagged an issue but gave no description."

    # If VERIFIED: yes but the model still filled in an ISSUE (contradictory
    # response), prefer the safer reading: treat it as not verified.
    if verified and issue_line and issue_line.upper() != "NONE":
        verified = False
        issue = issue_line

    return {"verified": verified, "issue": issue}


def verify_answer(answer_text, chunks, model="qwen2.5:7b-instruct"):
    """
    Check whether each citation in answer_text is actually supported by
    the matching chunk's text, and whether the answer's claims are
    grounded rather than invented.

    Args:
        answer_text: the generated answer text to check, including its
            "Sources:" line (as returned by generate_answer in
            generate.py).
        chunks: list of {"text", "case_name", "page_number"} dicts — the
            same chunks that were used to generate answer_text.
        model: name of the local Ollama model to call. Defaults to
            "qwen2.5:7b-instruct" per CONTRACTS.md — if you change this
            default, update it there and in every other function that
            defaults to the same model (rewrite_query, summarize_case,
            generate_answer).

    Returns:
        dict: {"verified": bool, "issue": str or None}. issue describes
        what's wrong if verified is False; issue is None if verified is
        True.
    """
    prompt = _build_verification_prompt(answer_text, chunks)

    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )

    return _parse_verification_response(response["message"]["content"])


def generate_verified_answer(question, chunks, model="qwen2.5:7b-instruct", progress_callback=None):
    """
    Generate an answer and verify it; retry generation ONCE (steered by
    the verification issue) if the first attempt fails verification. If
    still unverified after the retry, return a fixed fallback message
    rather than ever surfacing an unverified claim to the user.

    Args:
        question: the user's natural-language question.
        chunks: list of {"text", "case_name", "page_number"} dicts to
            generate and verify the answer against.
        model: name of the local Ollama model to call for both
            generation and verification. Defaults to
            "qwen2.5:7b-instruct" per CONTRACTS.md — if you change this
            default, update it there and in every other function that
            defaults to the same model (rewrite_query, summarize_case).

    Returns:
        dict: {"answer": str, "verified": bool} per CONTRACTS.md 3.4.
        verified is True only if generate_answer's output passed
        verify_answer, on either the first or second attempt. If both
        attempts fail verification, answer is a fixed "no verified
        answer" message and verified is False — this function never
        returns an answer that failed verification.
    """
    answer_text = generate_answer(question, chunks, model=model)
    result = verify_answer(answer_text, chunks, model=model)

    if result["verified"]:
        if progress_callback:
            progress_callback({"verified": True, "retrying": False})
        return {"answer": answer_text, "verified": True}

    # One retry, steered away from whatever verify_answer flagged.
    if progress_callback:
        progress_callback({"verified": False, "retrying": True, "issue": result["issue"]})
    retry_answer_text = generate_answer(
        question, chunks, model=model, failure_note=result["issue"]
    )
    retry_result = verify_answer(retry_answer_text, chunks, model=model)

    if retry_result["verified"]:
        if progress_callback:
            progress_callback({"verified": True, "retrying": False})
        return {"answer": retry_answer_text, "verified": True}

    if progress_callback:
        progress_callback({"verified": False, "retrying": False, "issue": retry_result["issue"]})
    return {
        "answer": "No verified answer could be found in the uploaded documents for this question.",
        "verified": False,
    }


if __name__ == "__main__":
    sample_chunks = [
        {
            "text": (
                "The court held that the defendant breached the implied covenant of "
                "good faith by unreasonably delaying performance under the contract."
            ),
            "case_name": "Smith_v_Jones_2019",
            "page_number": 4,
        },
        {
            "text": (
                "Damages were awarded in the amount of $42,000, reflecting the "
                "plaintiff's lost profits during the delay period."
            ),
            "case_name": "Smith_v_Jones_2019",
            "page_number": 7,
        },
    ]

    supported_answer = (
        "The court found the defendant breached the implied covenant of good faith by "
        "delaying performance, and awarded $42,000 in damages for the plaintiff's lost "
        "profits.\n\nSources: Smith_v_Jones_2019, p. 4; Smith_v_Jones_2019, p. 7"
    )
    unsupported_answer = (
        "The court awarded $500,000 in punitive damages due to fraud.\n\n"
        "Sources: Smith_v_Jones_2019, p. 4"
    )

    print("--- Verifying a grounded answer ---")
    print(verify_answer(supported_answer, sample_chunks))

    print("\n--- Verifying an unsupported answer ---")
    print(verify_answer(unsupported_answer, sample_chunks))
