import os
import re

import ollama


QUERY_TIMEOUT_SECONDS = float(os.getenv("OLLAMA_QUERY_TIMEOUT_SECONDS", "90"))


# Matches a Sources: line even when the model adds markdown decoration
# (e.g. **Sources:** or > Sources:).  Group 1 captures everything after
# the colon on that line.
_SOURCES_LINE_RE = re.compile(r"(?im)^[\s*_#>-]*Sources:[\s*_]*(.*)$")

# Matches a bare tag (C1) OR a bracket-wrapped tag ([C1]) in the answer
# body.  strip("[]") in the replacement removes the brackets before
# looking up in tag_map so the expansion is "[Smith, p. 4]", not
# "[[Smith, p. 4]]".
_INLINE_TAG_RE = re.compile(r"\[?\bC\d+\b\]?")

# Used only on the Sources line itself, where tags are never bracket-wrapped.
_TAG_RE = re.compile(r"\bC\d+\b")


def _assign_tags(chunks):
    """
    Assign each chunk a short tag (C1, C2, ...) in the order given, and
    build a lookup from tag -> the real (case_name, page_number) pair it
    stands for.

    Tags are positional, not persistent — they only need to be unique
    within a single prompt/response round trip, not across calls.

    Args:
        chunks: list of chunk dicts (contract 3.2 shape).

    Returns:
        tuple: (tag_map, tagged_chunks)
            tag_map: dict[str, dict] — {"C1": {"case_name": str,
                "page_number": int}, ...}
            tagged_chunks: list of (tag, chunk) pairs, same order as input.
    """
    tag_map = {}
    tagged_chunks = []
    for i, chunk in enumerate(chunks, start=1):
        tag = f"C{i}"
        tag_map[tag] = {
            "case_name": chunk["case_name"],
            "page_number": chunk["page_number"],
        }
        tagged_chunks.append((tag, chunk))
    return tag_map, tagged_chunks


def _expand_tagged_sources(answer_text, tag_map):
    """
    Replace a tag-based "Sources:" line (e.g. "Sources: C1, C3") with the
    real case_name/page_number citations it refers to, so everything
    downstream of generate_answer — verify_answer, the UI, CONTRACTS.md
    3.4 — still sees the same "Sources: <case_name>, p. <page>; ..."
    format it always has. The tag machinery is invisible outside this
    function; nothing else needs to know it exists.

    A tag the model wrote that isn't in tag_map (hallucinated, or a
    typo like "C12" when only 4 chunks exist) expands to an explicit
    "[unresolved citation: C12]" marker rather than being silently
    dropped or guessed at — verify_answer's citation-accuracy check
    then has something concrete to fail against, per the fail-closed
    principle, instead of a Sources line that looks clean but is
    quietly missing a claim's citation.

    Args:
        answer_text: raw model output, containing a tag-based
            "Sources:" line.
        tag_map: dict as returned by _assign_tags.

    Returns:
        str: answer_text with its Sources line's tags expanded. If no
        "Sources:" line is found, answer_text is returned unchanged —
        verify_answer will catch the missing line on its own.
    """
    match = _SOURCES_LINE_RE.search(answer_text)
    if not match:
        return answer_text

    tags_found = _TAG_RE.findall(match.group(1))
    if not tags_found:
        # A "Sources:" line exists but has no recognizable tags in it —
        # leave it as-is; verify_answer will flag it as unsupported.
        return answer_text

    expanded_citations = []
    for tag in tags_found:
        if tag in tag_map:
            entry = tag_map[tag]
            expanded_citations.append(f"{entry['case_name']}, p. {entry['page_number']}")
        else:
            expanded_citations.append(f"[unresolved citation: {tag}]")

    new_sources_line = "Sources: " + "; ".join(expanded_citations)

    # Expand inline [Cx] or Cx references in the body that appear BEFORE
    # the Sources line.  Use match.start() / match.end() (regex offsets)
    # rather than str.index("Sources:") so the split is always at the
    # right position even when the model wrote "SOURCES:" or decorated
    # the line with markdown.
    #
    # _INLINE_TAG_RE matches both bare "C1" and bracket-wrapped "[C1]".
    # strip("[]") removes the brackets before the tag_map lookup so the
    # replacement is "[Smith, p. 4]" not "[[Smith, p. 4]]".
    def _replace_inline(m):
        tag = m.group(0).strip("[]")
        if tag in tag_map:
            e = tag_map[tag]
            return f"[{e['case_name']}, p. {e['page_number']}]"
        return f"[unresolved citation: {tag}]"

    head = _INLINE_TAG_RE.sub(_replace_inline, answer_text[:match.start()])
    return head + new_sources_line + answer_text[match.end():]



import json

def build_answer_prompt(question, chunks, failure_note=None):
    """
    Build a prompt instructing an LLM to answer using ONLY the provided
    chunk excerpts, citing them by short tag (C1, C2, ...) rather than
    by case name/page number directly — the model never sees a page
    number it could copy wrong or invent, since it only has to echo a
    tag it was handed verbatim.

    Args:
        question: the user's natural-language question.
        chunks: list of dicts, each with at least {"text", "case_name",
            "page_number"}. May also carry "relevance_score" (ignored
            here, per CONTRACTS.md 3.2).
        failure_note: optional string describing what was wrong with a
            previous attempt, included as an explicit instruction not
            to repeat that mistake.

    Returns:
        tuple: (prompt, tag_map)
            prompt: str, ready to send to the LLM.
            tag_map: dict as returned by _assign_tags — the caller
            needs this to expand the model's tag-based Sources line
            back into real citations afterward.
    """
    tag_map, tagged_chunks = _assign_tags(chunks)

    # Build the closed list of valid tags for this call.
    valid_tags = [tag for tag, _ in tagged_chunks]
    valid_tag_list = ", ".join(valid_tags)

    _CHUNK_CHAR_LIMIT = 1200
    excerpt_blocks = []
    for tag, chunk in tagged_chunks:
        text = chunk["text"]
        if len(text) > _CHUNK_CHAR_LIMIT:
            text = text[:_CHUNK_CHAR_LIMIT] + "…"
        excerpt_blocks.append(f"[{tag}]\n{text}")
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
Do NOT mention, name, or reference any case that is not one of the excerpts shown \
below. If the excerpts do not contain enough information \
to answer the question, set "insufficient" to true.
{failure_note_block}
EXCERPTS:
\"\"\"
{excerpts_text}
\"\"\"

QUESTION:
{question}

CRITICAL FORMATTING INSTRUCTIONS:
You must return a strictly valid JSON object.
1. "insufficient" must be true if the excerpts cannot answer the question.
2. If sufficient, break your answer down into individual claims in "answer_claims". 
3. Every single claim MUST have a valid "tag" from this list: {valid_tag_list}.
4. Answer the user's actual question first, rather than listing case summaries.
5. For a request for a similar or analogous case, explain why each cited excerpt
   is relevant and state any material limitation or factual distinction.
6. Separate a court's holding or stated legal rule from facts, arguments, dicta,
   and a quotation of another case. Do not present a factual example as a rule.
7. When the question concerns forfeiture, deposits, penalties, or damages, make
   the answer explicit about (a) whether a breach/default occurred, (b) whether
   the excerpt addresses proof of loss, and (c) whether it supports full
   forfeiture or only reasonable compensation. Do not fill in any missing point.
8. If the excerpts support only a qualified answer, say so in a claim and cite
   the excerpt supporting the qualification.
9. Return ONLY the JSON object, nothing else.
"""

    return prompt, tag_map


def generate_answer_structured(question, chunks, model="qwen2.5:7b-instruct", failure_note=None):
    """
    Build the tag-based answer prompt, call a local Ollama model using JSON schema,
    render into the expected text format, and return both the expanded text and claims.
    """
    print(f"[generate_answer_structured] chunks={len(chunks)}, failure_note={'yes' if failure_note else 'no'}")
    prompt, tag_map = build_answer_prompt(question, chunks, failure_note=failure_note)

    valid_tags = list(tag_map.keys())
    schema = {
        "type": "object",
        "properties": {
            "answer_claims": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "claim": {"type": "string"},
                        "tag": {"type": "string", "enum": valid_tags}
                    },
                    "required": ["claim", "tag"]
                }
            },
            "insufficient": {"type": "boolean"}
        },
        "required": ["answer_claims", "insufficient"]
    }

    response = ollama.Client(timeout=QUERY_TIMEOUT_SECONDS).chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        options={"num_ctx": 8192, "temperature": 0, "num_predict": 300},
        format=schema,
        keep_alive="30m",
    )

    raw = response["message"]["content"]
    
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {"answer_claims": [], "insufficient": True}
        
    claims = data.get("answer_claims", [])
    insufficient = data.get("insufficient", False)
    
    if insufficient or not claims:
        expanded = "The excerpts do not contain enough information to answer the question."
    else:
        body_parts = []
        tags_used = []
        for c in claims:
            claim_text = c.get("claim", "").strip()
            tag = c.get("tag", "").strip()
            body_parts.append(f"{claim_text} [{tag}]")
            if tag:
                tags_used.append(tag)
                
        body = " ".join(body_parts)
        
        seen = set()
        unique_tags = []
        for t in tags_used:
            if t not in seen:
                seen.add(t)
                unique_tags.append(t)
                
        sources_line = "Sources: " + "; ".join(unique_tags)
        
        raw_text = body + "\n\n" + sources_line
        expanded = _expand_tagged_sources(raw_text, tag_map)
        
    return expanded, claims


def generate_answer(question, chunks, model="qwen2.5:7b-instruct", failure_note=None):
    """
    Thin wrapper around generate_answer_structured that returns only the text.
    """
    text, _ = generate_answer_structured(question, chunks, model=model, failure_note=failure_note)
    return text

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
    prompt, tag_map = build_answer_prompt("What damages did the plaintiff receive?", sample_chunks)
    print(prompt)
    print("\ntag_map:", tag_map)

    print("\n\n--- Calling Ollama (requires model pulled locally) ---")
    answer = generate_answer("What damages did the plaintiff receive?", sample_chunks)
    print(answer)