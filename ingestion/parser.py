"""
Page-level PDF text extraction using PyMuPDF (fitz).

No chunking here — that's a separate step downstream. This just gives you
one dict per non-blank page.
"""

import os
import re

import fitz  # PyMuPDF


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

            pages.append({
                "page_number": zero_indexed_page_num + 1,
                "text": text,
            })

    return pages


def chunk_pdf(pdf_path):
    """
    Extract a PDF's pages and split each page's text into paragraph-level
    chunks. Chunks never span across a page boundary — a paragraph that
    happens to be cut off by a page break stays split into two chunks,
    one per page.

    Args:
        pdf_path: path to the PDF file (str or os.PathLike).

    Returns:
        list[dict]: [{"text": str, "case_name": str, "page_number": int}, ...]
        case_name is the PDF's filename without its extension, e.g.
        "cases/Smith_v_Jones_2019.pdf" -> "Smith_v_Jones_2019".
    """
    case_name = os.path.splitext(os.path.basename(pdf_path))[0]

    pages = extract_pages(pdf_path)

    chunks = []
    for page in pages:
        # Split on one or more blank lines (handles \n\n, \n \n, \r\n\r\n, etc.)
        paragraphs = re.split(r"\n\s*\n", page["text"])

        for paragraph in paragraphs:
            if not paragraph or not paragraph.strip():
                continue

            chunks.append({
                "text": paragraph.strip(),
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
