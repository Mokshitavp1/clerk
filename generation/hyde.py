"""
HyDE (Hypothetical Document Embeddings) query rewriting.

Generates a short hypothetical excerpt of legal text that would answer the
user's question, so that excerpt — rather than the raw question — can be
embedded for retrieval. Legal case text and natural-language questions live
in different regions of embedding space; embedding something that looks
like the target document tends to retrieve better than embedding the
question itself.
"""

import ollama


def rewrite_query(question, model="qwen2.5:7b-instruct"):
    """
    Generate a short, hypothetical excerpt of legal text (under 100 words)
    that would answer the given question, written in the tone of legal
    case documents.

    This output is meant to be embedded for retrieval in place of the raw
    question — it is NOT shown to the user, and it is not guaranteed to be
    factually accurate (it's a hypothetical passage, not a real citation).

    Args:
        question: the user's natural-language question.
        model: name of the local Ollama model to call. Defaults to
            "qwen2.5:7b-instruct" per CONTRACTS.md — if you change this
            default, update it there and in every other function that
            defaults to the same model (summarize_case, generate_answer,
            verify_answer).

    Returns:
        str: the generated hypothetical excerpt text.
    """
    prompt = f"""You are a legal writing assistant. Given the question below, write a short, \
hypothetical excerpt of legal case text (under 100 words) that would plausibly \
answer it, written in the tone and style of a real court opinion (e.g. findings \
of fact, holdings, or damages language).

Do not answer the question directly or explain anything. Do not include a \
preamble, disclaimer, or note that this is hypothetical. Output ONLY the \
excerpt itself, as if it were pulled directly from a case document.

QUESTION:
\"\"\"
{question}
\"\"\"

HYPOTHETICAL EXCERPT (under 100 words):"""

    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )

    return response["message"]["content"]


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python hyde.py '<question>'")
        sys.exit(1)

    excerpt = rewrite_query(sys.argv[1])
    print("--- Hypothetical excerpt (for embedding, not display) ---")
    print(excerpt)
