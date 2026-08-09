"""
Prompt construction and LLM call for the final answer-generation stage.

Takes retrieved (and, per self_rag.py, already-graded) chunks and turns
them into a grounded, cited answer.
"""

import ollama


def build_answer_prompt(question, chunks, failure_note=None):
    """
    Build a prompt instructing an LLM to answer a question using ONLY the
    provided chunk excerpts, with a required "Sources:" line at the end.

    Args:
        question: the user's natural-language question.
        chunks: list of dicts, each with at least {"text", "case_name",
            "page_number"}. Per CONTRACTS.md 3.2, chunks may also carry a
            "relevance_score" key — that's fine, it's simply ignored here
            rather than stripped, since other functions downstream may
            still want it on the same chunk objects.
        failure_note: optional string describing what was wrong with a
            previous generation attempt (e.g. an unsupported citation).
            When provided, it's included as an explicit instruction not
            to repeat that mistake. This is how generate_answer's retry
            path (see generate_verified_answer in verifier.py) steers a
            second attempt away from a known failure mode.

    Returns:
        str: a complete prompt ready to send to the LLM.
    """
    excerpt_blocks = []
    for chunk in chunks:
        label = f"[{chunk['case_name']}, p. {chunk['page_number']}]"
        excerpt_blocks.append(f"{label}\n{chunk['text']}")
    excerpts_text = "\n\n".join(excerpt_blocks)

    failure_note_block = ""
    if failure_note:
        failure_note_block = f"""
IMPORTANT — a previous attempt at this answer had a problem: {failure_note}
Do not repeat that mistake in this answer.
"""

    prompt = f"""You are a legal research assistant. Answer the question below using ONLY \
the excerpts provided. Do not use any outside knowledge, and do not invent, assume, \
or infer facts, holdings, or figures that are not explicitly present in the excerpts. \
If the excerpts do not contain enough information to answer the question, say so \
plainly rather than guessing.
{failure_note_block}
EXCERPTS:
\"\"\"
{excerpts_text}
\"\"\"

QUESTION:
{question}

Write your answer using only the excerpts above. At the end of your answer, add a \
line starting with "Sources:" that lists every case name and page number you \
actually relied on to answer (format: "Sources: <case_name>, p. <page_number>; \
<case_name>, p. <page_number>"). Only list a source if you actually used it — do \
not list excerpts you didn't rely on.

ANSWER:"""

    return prompt


def generate_answer(question, chunks, model="qwen2.5:7b-instruct", failure_note=None):
    """
    Build the answer prompt and call a local Ollama model, returning the
    raw response text.

    Args:
        question: the user's natural-language question.
        chunks: list of {"text", "case_name", "page_number"} dicts (see
            build_answer_prompt for the full shape, including the
            tolerated extra "relevance_score" key).
        model: name of the local Ollama model to call. Defaults to
            "qwen2.5:7b-instruct" per CONTRACTS.md — if you change this
            default, update it there and in every other function that
            defaults to the same model (rewrite_query, summarize_case,
            verify_answer).
        failure_note: optional string describing what was wrong with a
            previous attempt, passed straight through to
            build_answer_prompt. See generate_verified_answer in
            verifier.py for how this gets used on a retry.

    Returns:
        str: the model's raw response text, including its trailing
        "Sources:" line. This is NOT parsed or verified here — that's
        verify_answer's job in verifier.py.
    """
    prompt = build_answer_prompt(question, chunks, failure_note=failure_note)

    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )

    return response["message"]["content"]


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

    print("--- Prompt (no failure_note) ---")
    print(build_answer_prompt("What damages did the plaintiff receive?", sample_chunks))

    print("\n\n--- Prompt (with failure_note) ---")
    print(build_answer_prompt(
        "What damages did the plaintiff receive?",
        sample_chunks,
        failure_note="Previous answer cited a page number that wasn't in the provided excerpts.",
    ))

    print("\n\n--- Calling Ollama (requires model pulled locally) ---")
    answer = generate_answer("What damages did the plaintiff receive?", sample_chunks)
    print(answer)
