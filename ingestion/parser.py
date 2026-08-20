"""
Page-level PDF text extraction using PyMuPDF (fitz).

No chunking here — that's a separate step downstream. This just gives you
one dict per non-blank page.
"""

import os
import re

import fitz  # PyMuPDF

# ---------------------------------------------------------------------------
# Indian Kanoon footer pattern
# ---------------------------------------------------------------------------
# Every IK page ends with (glued directly onto the last line of real content,
# no blank-line separator):
#
#   <case title line>
#   Indian Kanoon - http://indiankanoon.org/doc/<id>/
#   <bare page number, e.g. "3">
#
# The footer can be 2–3 trailing lines.  We strip them before chunking so
# they don't pollute any chunk's text field.
_IK_FOOTER_RE = re.compile(
    r"(?:\n[^\n]*){0,1}"             # optional case-title line (may be partial)
    r"\nIndian Kanoon\s*-\s*http://indiankanoon\.org/doc/[^\n]+"
    r"\n\d+\s*$",                    # bare page-number line at end of string
    re.IGNORECASE,
)


def _strip_ik_footer(text):
    """Remove the Indian Kanoon footer from the end of a page's raw text.

    Strips up to three trailing lines matching the pattern:
        <case title>\nIndian Kanoon - http://...\n<page number>

    If no footer is found the text is returned unchanged.
    """
    stripped = _IK_FOOTER_RE.sub("", text)
    # Fallback: if the above didn't match, still nuke a bare trailing line
    # that is *only* the IK URL (sometimes the case-title is absent).
    if stripped == text:
        stripped = re.sub(
            r"\nIndian Kanoon\s*-\s*http://indiankanoon\.org/doc/[^\n]+\n\d+\s*$",
            "",
            text,
            flags=re.IGNORECASE,
        )
    return stripped


# ---------------------------------------------------------------------------
# Sentence-boundary sliding-window chunker
# ---------------------------------------------------------------------------
_SENTENCE_END_RE = re.compile(r"(?<=[.!?])\s+")


def _split_sentences(text):
    """Split *text* into a list of sentence strings using punctuation cues.

    Falls back to splitting on single newlines when no sentence-ending
    punctuation is present (common in Indian Kanoon header/paragraph text).
    """
    # Normalise internal line-breaks to spaces so the sentence splitter
    # works across soft-wrapped lines.
    normalised = re.sub(r"\n+", " ", text).strip()
    sentences = _SENTENCE_END_RE.split(normalised)
    # Remove empties produced by leading/trailing whitespace.
    return [s.strip() for s in sentences if s.strip()]


def _window_sentences(sentences, target_words=200, overlap_words=25):
    """Yield (start_idx, end_idx) index pairs over *sentences* such that
    each window contains roughly *target_words* words and consecutive
    windows share approximately *overlap_words* words of context.

    Chunks never break mid-sentence — a sentence is always kept whole
    inside one window.
    """
    if not sentences:
        return

    word_counts = [len(s.split()) for s in sentences]
    total = len(sentences)
    i = 0  # first sentence of the current window

    while i < total:
        j = i  # candidate end (exclusive)
        words_so_far = 0

        # Grow the window until we hit the target or run out of sentences.
        while j < total and words_so_far < target_words:
            words_so_far += word_counts[j]
            j += 1

        yield (i, j)

        if j >= total:
            break  # last window; we're done

        # Walk *back* from j to find the overlap start for the next window.
        overlap = 0
        k = j - 1
        while k > i and overlap < overlap_words:
            overlap += word_counts[k]
            k -= 1
        # k+1 is the first sentence of the overlap region.
        i = k + 1  # advance, but keep overlap sentences in next window


def extract_pages(pdf_path):
    """
    Open a PDF and return a list of dicts, one per non-blank page:
        {"page_number": int, "text": str}

    page_number starts at 1 (not 0-indexed like PyMuPDF internally uses).
    Pages that are blank or whitespace-only after extraction are skipped
    entirely — they do not get an entry, and no placeholder is inserted,
    so page_number values may not be contiguous.

    Args:
        pdf_path: path to the PDF file (str or os.PathLike).

    Returns:
        list[dict]: [{"page_number": 1, "text": "..."}, ...]

    Raises:
        FileNotFoundError: if pdf_path does not exist.
        fitz.FileDataError: if the file exists but isn't a valid PDF.
    """
    pages = []

    with fitz.open(pdf_path) as doc:
        for zero_indexed_page_num, page in enumerate(doc):
            text = page.get_text()

            if not text or not text.strip():
                continue

            # Strip Indian Kanoon footer before storing, so downstream
            # chunking doesn't absorb case-title / URL / page-number noise.
            text = _strip_ik_footer(text)

            if not text.strip():
                continue

            pages.append({
                "page_number": zero_indexed_page_num + 1,
                "text": text,
            })

    return pages


def chunk_pdf(pdf_path, target_words=200, overlap_words=25):
    """
    Extract a PDF's pages and split each page's text into fixed-size chunks
    aligned to sentence boundaries.

    Blank-line paragraph splitting is intentionally NOT used here: Indian
    Kanoon PDFs (and many other sources) contain no blank-line breaks inside
    page text, so that strategy collapses every page into a single chunk and
    destroys retrieval granularity.

    Strategy
    --------
    1. Normalise each page's text: collapse single newlines (soft-wraps) into
       spaces, then split into sentences on sentence-ending punctuation.
    2. Slide a window of *target_words* words over the sentence list, keeping
       *overlap_words* words of context in the next window so a fact split
       across a boundary isn't lost from either chunk.
    3. Chunks never cross a page boundary.

    Args:
        pdf_path:      path to the PDF file (str or os.PathLike).
        target_words:  approximate word-count ceiling per chunk (default 200).
        overlap_words: approximate word-count overlap between consecutive
                       chunks on the same page (default 25).

    Returns:
        list[dict]: [{"text": str, "case_name": str, "page_number": int}, ...]
        case_name is the PDF's filename without its extension, e.g.
        "cases/Smith_v_Jones_2019.pdf" -> "Smith_v_Jones_2019".
    """
    case_name = os.path.splitext(os.path.basename(pdf_path))[0]

    pages = extract_pages(pdf_path)

    chunks = []
    for page in pages:
        sentences = _split_sentences(page["text"])
        if not sentences:
            continue

        for start, end in _window_sentences(sentences, target_words, overlap_words):
            window_text = " ".join(sentences[start:end]).strip()
            if not window_text:
                continue

            chunks.append({
                "text": window_text,
                "case_name": case_name,
                "page_number": page["page_number"],
            })

    return chunks


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python pdf_extract.py <path_to_pdf>")
        sys.exit(1)

    result = chunk_pdf(sys.argv[1])
    print(f"Extracted {len(result)} chunk(s).")
    for c in result[:3]:
        preview = c["text"][:120].replace("\n", " ")
        print(f"  [{c['case_name']} p.{c['page_number']}] {preview}...")
