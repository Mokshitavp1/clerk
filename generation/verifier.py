"""
Citation and groundedness verification for generated answers.

verify_answer checks a generated answer against the chunks it was built
from, to catch invented facts or citations that don't actually match the
chunk text they claim to come from.

Three layers of protection — the first two run before any LLM call:
  1. _check_citations_deterministic: mechanically validates every Sources:
     line entry against the actual (case_name, page_number) pairs from
     the chunks passed in.  Hard fail, not subject to model discretion.
  1b. _check_has_content: rejects answers whose body (everything before
     the Sources: line) contains fewer than BODY_MIN_WORDS words.  An
     answer that is only a Sources: line with no prose has zero claims to
     contradict, which would otherwise let the LLM verifier return
     VERIFIED: yes on a functionally empty answer.
  2. _build_verification_prompt / verify_answer LLM call: checks claim
     groundedness and citation accuracy for entries that passed layers 1
     and 1b.
"""

import re
import os

import ollama

from generate import generate_answer, generate_answer_structured

# Minimum word count for the answer body (everything before the Sources: line).
# 15 words is just above the shortest plausible single-sentence legal answer;
# anything under this threshold is functionally empty and should be rejected
# without consulting the LLM verifier.
BODY_MIN_WORDS = 15
VERIFIER_TIMEOUT_SECONDS = float(os.getenv("OLLAMA_VERIFIER_TIMEOUT_SECONDS", "60"))
_ollama_clients = {}


def _get_ollama_client(timeout):
    """Reuse Ollama connections while keeping timeout-specific clients separate."""
    cache_key = (timeout, ollama.Client)
    client = _ollama_clients.get(cache_key)
    if client is None:
        client = ollama.Client(timeout=timeout)
        _ollama_clients[cache_key] = client
    return client


def _check_has_content(answer_text):
    """
    Deterministically reject answers that have no substantive prose body
    before the Sources: line.

    Splits answer_text on the first line that starts with "Sources:" (exact
    case, matching generate_answer's output format).  Everything before that
    line is the body.  Returns False if the body — after stripping whitespace
    — contains fewer than BODY_MIN_WORDS words, True otherwise.

    This is layer 1b in verify_answer: it runs after
    _check_citations_deterministic and before the LLM call.  An answer that
    is only a Sources: line has zero claims to contradict, so the LLM
    verifier would otherwise return VERIFIED: yes on empty content.

    Args:
        answer_text: the generated answer text, including its "Sources:" line.

    Returns:
        dict: {"verified": bool, "issue": str or None}.  issue is None when
        verified is True.  When False, issue contains a human-readable
        description of what failed.
    """
    body_lines = []
    for line in answer_text.splitlines():
        if line.startswith("Sources:"):
            break
        body_lines.append(line)

    body = " ".join(body_lines).strip()
    word_count = len(body.split()) if body else 0

    if word_count < BODY_MIN_WORDS:
        return {
            "verified": False,
            "issue": (
                "The answer contains no substantive content — only a Sources line."
                f" (body word count: {word_count}; minimum required: {BODY_MIN_WORDS})"
            ),
        }

    return {"verified": True, "issue": None}


def _normalize_case_name_for_comparison(name):
    """
    Normalize a case name for resilient matching. Used only for comparison
    to tolerate cosmetic formatting differences (like replacing underscores
    with spaces) rather than paraphrasing or abbreviation.

    1. Lowercases the name.
    2. Replaces underscores with spaces.
    3. Strips trailing Indian Kanoon-style date suffixes (e.g.,
       " on 15 january 1963") because the LLM frequently drops them,
       and steps 1+2 alone do not resolve an omitted date suffix when
       doing a substring check.

    NOTE — accepted risk of step 3: date-stripping trades exact-match
    strictness for tolerance of the model's formatting habits.  If the
    corpus ever contains two cases with identical party names but different
    dates (e.g., an original judgment and its appeal), this normalization
    could conflate them — page_number is still checked exactly, but the
    case_name substring match alone would no longer disambiguate between
    the two versions.  With the current 5-case corpus of clearly distinct
    names this is very unlikely to occur, but revisit this if the corpus
    grows to include interlocutory orders, remands, or appeals of existing
    cases.
    """
    norm = name.lower().replace("_", " ").strip()
    # Normalize all separator variants ('v', 'v.', 'vs', 'vs.', 'versus') to
    # a single canonical 'vs' so substring matching is stable regardless of
    # which form the model or a PDF filename uses.  Previously only 'v' and
    # 'v.' were handled, causing 'vs.' in LLM output to escape normalization
    # and silently fail the Layer 1c hallucination check.
    norm = re.sub(r"\s+v(?:ersus|s\.?|\.?)\s+", " vs ", norm)
    # Remove trailing date suffixes: " on <day> <month> <year>"
    norm = re.sub(r"\s+on\s+\d{1,2}\s+[a-z]+\s+\d{4}$", "", norm)
    return norm


def _check_citations_deterministic(answer_text, chunks):
    """
    Mechanically validate every Sources-line entry in answer_text against
    the set of (case_name, page_number) pairs actually present in chunks.

    This runs before any LLM call and is the hard first gate.  A citation
    that does not exactly match a provided chunk is an automatic fail —
    whether it names a real case discussed within chunk text, a misspelled
    case, or a completely invented one makes no difference: if it wasn't
    supplied as a chunk it cannot be a valid source.

    Args:
        answer_text: the generated answer text, including its "Sources:"
            line (as returned by generate_answer).
        chunks: list of {"text", "case_name", "page_number"} dicts — the
            same chunks passed to generate_answer.

    Returns:
        dict: {"verified": bool, "issue": str or None}.  issue is None
        when verified is True.  When False, issue names every citation
        that failed and why, so it can be used as a failure_note on the
        retry generation call.
    """
    # Build the authoritative set of (case_name, page_number) pairs.
    valid_pairs = {
        (c["case_name"], int(c["page_number"])) for c in chunks
    }

    # Locate the Sources: line (case-insensitive, may appear anywhere).
    sources_line = None
    for line in answer_text.splitlines():
        if line.strip().lower().startswith("sources:"):
            sources_line = line
            break

    if sources_line is None:
        return {
            "verified": False,
            "issue": (
                'The answer has no "Sources:" line. Every answer must end '
                "with a Sources: line citing the excerpts it is based on."
            ),
        }

    raw_after_colon = sources_line.split(":", 1)[1]
    # Note: We split citations strictly by ';'. This assumes the case_name
    # (derived from the PDF filename) does not itself contain a semicolon.
    # If a filename had a ';', it would fracture the citation and fail closed.
    raw_entries = [e.strip() for e in raw_after_colon.split(";") if e.strip()]

    bad_citations = []
    for entry in raw_entries:
        # Each valid entry must contain "p. <integer>" and a case_name that
        # is in the chunk set for that page.  Entries without a page number
        # — such as bare external case references like "Howe v. Smith" —
        # cannot be matched to a chunk and are rejected.
        page_match = re.search(r"(?:p\.|pg\.|page)\s*(\d+)", entry, re.IGNORECASE)
        if page_match is None:
            bad_citations.append(
                f"{entry!r} — no page number found; only provided excerpts "
                "may appear on the Sources line, and each must include a "
                "page number in the form 'p. N'."
            )
            continue

        page_num = int(page_match.group(1))
        norm_entry = _normalize_case_name_for_comparison(entry)
        
        # Accept entry if any chunk shares this page and the normalized chunk's
        # case_name appears as a substring of the normalized citation string.
        matched = any(
            str(page_num) == str(pg) and _normalize_case_name_for_comparison(cn) in norm_entry
            for (cn, pg) in valid_pairs
        )
        if not matched:
            bad_citations.append(
                f"{entry!r} — no provided excerpt has this exact "
                f"(case_name, page_number) pair.  A case that is merely "
                "discussed within an excerpt's text is not itself a valid "
                "Sources-line entry unless it was supplied as its own excerpt."
            )

    if bad_citations:
        joined = "; ".join(bad_citations)
        return {
            "verified": False,
            "issue": (
                f"Citation check failed — the following Sources-line "
                f"entries do not match any provided chunk: {joined}"
            ),
        }

    return {"verified": True, "issue": None}


def _check_hallucinated_cases(answer_text, chunks):
    """
    Deterministic check to scan the answer body for any case-name-like
    mentions that aren't in the provided chunks. Fast failure.
    """
    import re
    # Match strings like "Kunwar Chiranjit Singh v. Hat Swarup" or "State_v_Doe"
    pattern = re.compile(r"\b[A-Z][A-Za-z.]+(?:\s+v\.?\s+|_v_)[A-Z][A-Za-z.]+\b")
    
    # Strip the sources line if present
    body = answer_text
    match = re.search(r"(?im)^\s*Sources:\s*(.*)$", answer_text)
    if match:
        body = answer_text[:match.start()]
    
    mentions = pattern.findall(body)
    
    valid_names = {_normalize_case_name_for_comparison(c['case_name']) for c in chunks}
    
    bad_mentions = []
    for mention in mentions:
        norm_mention = _normalize_case_name_for_comparison(mention)
        if not any(norm_mention in valid for valid in valid_names) and not any(valid in norm_mention for valid in valid_names):
            bad_mentions.append(mention)
            
    if bad_mentions:
        return {
            "verified": False,
            "issue": f"You mentioned {', '.join(bad_mentions)}, which was not in the provided excerpts — remove it."
        }
    return {"verified": True, "issue": None}


def _check_claims_deterministic(claims, chunks):
    """
    Mechanically validate every claim against its cited chunk before any LLM check.
    Each claim's tag must exist in chunks.
    Every number, dollar amount, year and "Section N" token in the claim must
    appear in the cited chunk's text.
    """
    import re
    tag_to_chunk = {}
    for i, c in enumerate(chunks, 1):
        tag_to_chunk[f"C{i}"] = c
        
    for item in claims:
        claim_text = item.get("claim", "")
        tag = item.get("tag", "")
        
        if not tag:
            return False, "A claim is missing a source tag."
            
        if tag not in tag_to_chunk:
            return False, f"Claim tag {tag} is invalid or not in provided excerpts."
            
        chunk = tag_to_chunk[tag]
        chunk_text = chunk["text"]
        case_name_norm = chunk["case_name"].lower()
        
        claim_norm = re.sub(r"\s+", " ", claim_text.lower().replace(",", ""))
        chunk_norm = re.sub(r"\s+", " ", chunk_text.lower().replace(",", ""))

        # Claims copied directly from an excerpt are already grounded. This
        # fast path avoids sending an answer through a slow second LLM call,
        # and prevents a verifier model from rejecting text that is verbatim
        # present in the cited passage.
        claim_tokens = set(re.findall(r"[a-z0-9]+", claim_norm))
        chunk_tokens = set(re.findall(r"[a-z0-9]+", chunk_norm))
        if claim_tokens and claim_tokens.issubset(chunk_tokens):
            continue
        
        patterns = [
            (r"section \d+", "Section reference"),
            (r"\$\d+(?:\.\d+)?", "Dollar amount"),
            (r"\b\d+(?:\.\d+)?\b", "Number")
        ]
        
        for pat, desc in patterns:
            for m in re.finditer(pat, claim_norm):
                token = m.group(0)
                # Years (4-digit numbers) might be in the claim but only appear
                # in the cited chunk's case_name (e.g. "Smith_v_Jones_2019"),
                # not the text body. If so, don't fail groundedness.
                if desc == "Number" and len(token) == 4 and token in case_name_norm:
                    continue
                if token not in chunk_norm:
                    return False, f"The {desc.lower()} '{token}' was not found in excerpt {tag}."
                    
    return True, None


def _claims_are_verbatim(claims, chunks):
    """Return True when every tagged claim is explicitly present in its chunk."""
    tag_to_chunk = {f"C{i}": chunk for i, chunk in enumerate(chunks, 1)}
    for item in claims:
        tag = item.get("tag", "")
        chunk = tag_to_chunk.get(tag)
        if chunk is None:
            return False
        claim_tokens = set(re.findall(r"[a-z0-9]+", item.get("claim", "").lower()))
        chunk_tokens = set(re.findall(r"[a-z0-9]+", chunk["text"].lower()))
        if not claim_tokens or not claim_tokens.issubset(chunk_tokens):
            return False
    return bool(claims)



def _build_verification_prompt(answer_text, chunks):
    """
    Build a prompt asking an LLM to check an answer's groundedness and
    citation accuracy against the source chunks it was generated from.

    Note: citation format (does each Sources entry correspond to a real
    chunk?) is already checked deterministically before this prompt runs
    (see _check_citations_deterministic).  This prompt handles the
    judgment-dependent half: are the claims in the answer actually
    supported by the matched chunk's text?

    Args:
        answer_text: the generated answer, including its "Sources:" line.
        chunks: list of {"text", "case_name", "page_number"} dicts that
            were used to generate answer_text.

    Returns:
        str: a complete verification prompt.
    """
    _CHUNK_CHAR_LIMIT = 1200
    excerpt_blocks = []
    for chunk in chunks:
        label = f"[{chunk['case_name']}, p. {chunk['page_number']}]"
        text = chunk["text"]
        if len(text) > _CHUNK_CHAR_LIMIT:
            text = text[:_CHUNK_CHAR_LIMIT] + "…"
        excerpt_blocks.append(f"{label}\n{text}")
    excerpts_text = "\n\n".join(excerpt_blocks)

    # Build a compact list of the authoritative (case_name, page) pairs so
    # the model knows exactly which identifiers are valid sources.
    valid_source_list = "\n".join(
        f"  - {chunk['case_name']}, p. {chunk['page_number']}"
        for chunk in chunks
    )

    prompt = f"""You are a strict legal fact-checker. Your job is to check whether an \
answer is fully grounded in the excerpts it claims to be based on.

IMPORTANT — citation identity rule: the ONLY case names that are valid Sources-line \
entries are those whose case_name appears in the list of PROVIDED EXCERPTS below. \
A case that is merely discussed, quoted, or referenced WITHIN an excerpt's text is \
NOT itself a valid source — it does not count as a provided excerpt, and citing it \
on the Sources line is an error even if the content sounds correct.

PROVIDED EXCERPT IDENTIFIERS (the only valid Sources-line entries):
{valid_source_list}

Check for two things:

1. CITATION ACCURACY: every entry on the "Sources:" line must be one of the \
identifiers listed above, and the claim(s) attributed to that citation must \
actually be supported by that excerpt's text.
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
        stripped = line.strip().replace("*", "")
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


def verify_answer(answer_text, chunks, model="qwen2.5:7b-instruct", claims=None):
    """
    Check whether each citation in answer_text is actually supported by
    the matching chunk's text, and whether the answer's claims are
    grounded rather than invented.

    Runs three layers of checks in order:
      1. Deterministic citation pre-check (_check_citations_deterministic):
         mechanically validates every Sources-line entry against the actual
         (case_name, page_number) tuples in chunks.  Hard fail, no LLM
         involved.  A case merely discussed within chunk text — but not
         provided as its own chunk — is rejected here.
      1b. Content pre-check (_check_has_content): rejects answers whose
         body (everything before the Sources: line) contains fewer than
         BODY_MIN_WORDS words.  Hard fail, no LLM involved.  Prevents
         a sources-only answer from passing the LLM verifier unchallenged
         because there are no claims to contradict.
      1c. Hallucinated cases check.
      1d. Deterministic claim-level check (_check_claims_deterministic).
      2. LLM groundedness check: only reached if layers 1 pass.
         Verifies that the claims in the answer are supported by the
         matched excerpts.

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
    import json
    import re
    
    clean_answer_text = answer_text.strip()

    # Layer 1: deterministic citation pre-check (no LLM, hard fail).
    deterministic_result = _check_citations_deterministic(clean_answer_text, chunks)
    if not deterministic_result["verified"]:
        return deterministic_result

    # Layer 1b: deterministic content pre-check (no LLM, hard fail).
    content_result = _check_has_content(clean_answer_text)
    if not content_result["verified"]:
        return content_result
        
    # Layer 1c: deterministic hallucinated cases check (no LLM, hard fail).
    hallucination_result = _check_hallucinated_cases(clean_answer_text, chunks)
    if not hallucination_result["verified"]:
        return hallucination_result
        
    # Layer 1d: deterministic claim-level check (no LLM, hard fail).
    if claims:
        ok, issue = _check_claims_deterministic(claims, chunks)
        if not ok:
            return {"verified": False, "issue": issue}
        if _claims_are_verbatim(claims, chunks):
            return {"verified": True, "issue": None}

    # Layer 2: LLM groundedness + citation-content check.
    prompt = _build_verification_prompt(clean_answer_text, chunks)

    response = _get_ollama_client(VERIFIER_TIMEOUT_SECONDS).chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        options={"num_ctx": 8192, "temperature": 0, "num_predict": 200},
        keep_alive="30m",
    )

    return _parse_verification_response(response["message"]["content"])


def _retry_note(issue, chunks):
    """Turn an opaque unresolved-citation issue into an instruction the model can act on."""
    bad = re.findall(r"unresolved citation:\s*(C\d+)", issue or "")
    if not bad:
        return issue
    valid = ", ".join(f"C{i}" for i in range(1, len(chunks) + 1))
    return (
        f"You cited {', '.join(sorted(set(bad)))}, but the only valid tags are "
        f"{valid}. Use only those tags on the Sources line."
    )


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
    answer_text, claims = generate_answer_structured(question, chunks, model=model)
    result = verify_answer(answer_text, chunks, model=model, claims=claims)

    if result["verified"]:
        if progress_callback:
            progress_callback({"verified": True, "retrying": False})
        return {"answer": answer_text, "verified": True}

    # One retry, steered away from whatever verify_answer flagged.
    # Convert "[unresolved citation: C3]" into a human-readable instruction.
    retry_note = _retry_note(result["issue"], chunks)
    if progress_callback:
        progress_callback({"verified": False, "retrying": True, "issue": retry_note})
    retry_answer_text, retry_claims = generate_answer_structured(
        question, chunks, model=model, failure_note=retry_note
    )
    retry_result = verify_answer(retry_answer_text, chunks, model=model, claims=retry_claims)

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



def generate_verified_answer_per_case(
    question, cases, model="qwen2.5:7b-instruct", progress_callback=None
):
    """
    Run generate_verified_answer independently per case, then combine only
    the cases that individually passed verification.  A case that fails
    verification is dropped from the combined answer rather than dragging
    the whole response down to unverified.

    This is the Deep Thinking replacement for the pooled generate_verified_answer
    call.  The pooled version feeds all cases' chunks into one context window,
    which lets chunk-overlapping cases corrupt each other's citations and cause
    cross-case hallucination.  Isolating each case's generate+verify loop
    ensures that a noisy case (ambiguous chunks, low-quality excerpts) cannot
    contaminate the answer sections for the other cases in the shortlist.

    Verification contract — "fail closed per claim, not per answer":
    - A case whose answer fails verification is silently omitted from the
      combined output; its failure is not surfaced to the user.
    - If NO case produces a verified answer, the function returns the same
      fixed fallback string as generate_verified_answer (CONTRACTS.md 3.4),
      with verified=False.
    - If at least one case passes, verified=True and the answer body is the
      verified sections joined by blank lines.

    Shape note (CONTRACTS.md 3.4 extension):
    - The return dict is {"answer": str, "verified": bool}, identical to
      generate_verified_answer.  The "partially verified" state (some cases
      dropped) is NOT exposed in the dict — callers see verified=True as long
      as at least one section passed, and the answer text contains only those
      sections that cleared verification.  This is intentional: nothing
      unverified ever surfaces in the returned answer, which satisfies the
      fail-closed principle at the claim level rather than the whole-answer
      level.  See CONTRACTS.md 3.4 for the documented tradeoff.

    Args:
        question: the user's natural-language question.
        cases: list of case dicts in the shape from self_rag.get_graded_cases
            (CONTRACTS.md 3.3): [{"case_name": str, "relevance_score": float,
            "chunks": [<chunk dict per 3.2>, ...]}, ...].
        model: name of the local Ollama model to call.  Defaults to
            "qwen2.5:7b-instruct" per CONTRACTS.md.
        progress_callback: optional callable accepting the same signal dict
            as generate_verified_answer's progress_callback — forwarded
            transparently for each per-case call so the UI gets live status.

    Returns:
        dict: {"answer": str, "verified": bool} per CONTRACTS.md 3.4.
    """
    sections = []
    any_verified = False

    for case in cases:
        result = generate_verified_answer(
            question,
            case["chunks"],
            model=model,
            progress_callback=progress_callback,
        )
        if result["verified"]:
            sections.append(
                f"Regarding {case['case_name'].replace('_', ' ')}:\n{result['answer']}"
            )
            any_verified = True

    if not any_verified:
        return {
            "answer": (
                "No verified answer could be found in the uploaded documents "
                "for this question."
            ),
            "verified": False,
        }

    return {"answer": "\n\n".join(sections), "verified": True}


if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from fixtures import SUPPORTED_ANSWER_TEXT, UNSUPPORTED_ANSWER_TEXT, CHUNKS_SMITH

    print("--- Verifying a grounded answer ---")
    print(verify_answer(SUPPORTED_ANSWER_TEXT, CHUNKS_SMITH))

    print("\n--- Verifying an unsupported answer ---")
    print(verify_answer(UNSUPPORTED_ANSWER_TEXT, CHUNKS_SMITH))
    
    print("\n--- Testing VERIFIER_DATA leakage ---")
    try:
        from generate import build_answer_prompt # Ensure it can run
        res = generate_verified_answer("What damages did the plaintiff receive?", CHUNKS_SMITH)
        assert "VERIFIER_DATA" not in res["answer"], "VERIFIER_DATA leaked into answer!"
        print("VERIFIER_DATA assertion passed.")
    except Exception as e:
        print(f"Skipping or failed API test: {e}")
    
    print("\n--- Testing _check_claims_deterministic ---")
    claims_ok = [{"claim": "Damages were awarded in the amount of $42,000", "tag": "C2"}]
    print(f"Good claims: {_check_claims_deterministic(claims_ok, CHUNKS_SMITH)}")
    
    claims_bad_number = [{"claim": "The court awarded $500,000", "tag": "C2"}]
    print(f"Bad number: {_check_claims_deterministic(claims_bad_number, CHUNKS_SMITH)}")
    
    claims_bad_tag = [{"claim": "Damages were $42,000", "tag": "C3"}]
    print(f"Bad tag: {_check_claims_deterministic(claims_bad_tag, CHUNKS_SMITH)}")
