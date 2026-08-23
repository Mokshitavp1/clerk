"""
Prompt construction and LLM call for the case-summarization stage.
"""

import ollama

WORD_LIMIT = 6000   # total word budget sent to the LLM
HEAD_WORDS = 3000   # words taken from the beginning of the document
TAIL_WORDS = 3000   # words taken from the end of the document


def build_summary_prompt(case_text):
    """
    Build a prompt instructing an LLM to summarize a legal case in under
    150 words, covering: what the case concerns, the holding/outcome, and
    key facts — grounded only in the provided text.

    Truncation strategy: when a document exceeds WORD_LIMIT words, the
    function retains the first HEAD_WORDS words **and** the last TAIL_WORDS
    words, separated by a clear marker.  This prevents the naive head-only
    cut that previously dropped the court's final holding (which is often
    stated only in the last few paragraphs of a long judgment).

    Args:
        case_text: full (or partial) text of the case to summarize.

    Returns:
        str: a complete prompt ready to send to the LLM.
    """
    words = case_text.split()
    if len(words) > WORD_LIMIT:
        head = " ".join(words[:HEAD_WORDS])
        tail = " ".join(words[-TAIL_WORDS:])
        case_text = (
            head
            + "\n\n[... MIDDLE OF DOCUMENT OMITTED FOR BREVITY ...]\n\n"
            + tail
        )

    prompt = f"""You are a legal assistant. Summarize the following legal case in under 150 words.

Your summary must cover:
1. What the case concerns (the general subject matter/dispute)
2. The holding or outcome — in particular, focus on the court's **final ruling** on the main issue (e.g. the specific legal test applied, the statutory interpretation adopted, or the relief granted)
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
