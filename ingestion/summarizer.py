"""
Prompt construction and LLM call for the case-summarization stage.
"""

import ollama

WORD_LIMIT = 6000  # approx. words before truncation kicks in


def build_summary_prompt(case_text):
    """
    Build a prompt instructing an LLM to summarize a legal case in under
    150 words, covering: what the case concerns, the holding/outcome, and
    key facts — grounded only in the provided text.

    KNOWN LIMITATION: for very long documents (roughly 6000+ words), the
    text is truncated before being inserted into the prompt. This is a
    naive word-count truncation, not a smart/semantic one, so it may cut
    off mid-sentence and could drop material from later in the document
    (e.g. the final holding, if it's stated only at the end). A proper
    fix would involve chunking + map-reduce summarization instead of a
    single truncated prompt, but that's out of scope for this function.

    Args:
        case_text: full (or partial) text of the case to summarize.

    Returns:
        str: a complete prompt ready to send to the LLM.
    """
    words = case_text.split()
    if len(words) > WORD_LIMIT:
        case_text = " ".join(words[:WORD_LIMIT])
        case_text += "\n\n[TRUNCATED: document exceeded 6000 words; text cut off above]"

    prompt = f"""You are a legal assistant. Summarize the following legal case in under 150 words.

Your summary must cover:
1. What the case concerns (the general subject matter/dispute)
2. The holding or outcome (how the court ruled)
3. Key facts relevant to the outcome

Base your summary ONLY on the text provided below. Do not add information, case law, or context that isn't present in the text. If the provided text doesn't contain enough information for any of the three points above, say so briefly rather than inventing details.

CASE TEXT:
\"\"\"
{case_text}
\"\"\"

SUMMARY (under 150 words):"""

    return prompt


def summarize_case(chunks, model="qwen2.5:7b-instruct"):
    """
    Summarize one case from its chunks by joining their text, building a
    summary prompt, and calling a local Ollama model.

    Args:
        chunks: list of dicts belonging to a single case, each with at
            least {"text": str, "page_number": int}. Order is preserved
            as given — callers should pass chunks already sorted by
            page_number if reading order matters.
        model: name of the local Ollama model to call. Defaults to
            "qwen2.5:7b-instruct" per CONTRACTS.md — if you change this
            default, update it there and in every other function that
            defaults to the same model (rewrite_query, generate_answer,
            verify_answer).

    Returns:
        str: the model's summary text.
    """
    case_text = "\n\n".join(chunk["text"] for chunk in chunks)
    prompt = build_summary_prompt(case_text)

    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )

    return response["message"]["content"]


if __name__ == "__main__":
    sample_chunks = [
        {
            "text": (
                "In Smith v. Jones, the plaintiff alleged breach of contract "
                "after the defendant delayed delivery of goods by six months."
            ),
            "page_number": 1,
        },
        {
            "text": (
                "The court found that the delay, combined with the "
                "defendant's failure to notify the plaintiff in advance, "
                "constituted a breach of the implied covenant of good faith."
            ),
            "page_number": 4,
        },
        {
            "text": (
                "Damages of $42,000 were awarded to cover the plaintiff's "
                "lost profits during the delay period."
            ),
            "page_number": 7,
        },
    ]

    print("--- Prompt preview ---")
    print(build_summary_prompt(" ".join(c["text"] for c in sample_chunks)))

    print("\n--- Calling Ollama (requires model pulled locally) ---")
    summary = summarize_case(sample_chunks)
    print(summary)
