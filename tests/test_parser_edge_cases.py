"""
T9 — Scanned / corrupted PDFs.

TestCorruptedPDF runs immediately, no fixtures needed -- it generates a
broken "PDF" (garbage bytes with a .pdf extension) on the fly and checks
parser.py fails loudly rather than silently producing empty/garbage chunks.

TestScannedPDF needs a REAL scanned/OCR'd opinion PDF, since that failure
mode (garbled but non-empty text, or an image-only page PyMuPDF can't
extract text from at all) can't be faked with synthetic bytes. Steps:

    1. Go to https://www.courtlistener.com/ and search for an older
       (pre-1990) opinion -- these are more likely to be scanned/OCR'd
       rather than text-native PDFs.
    2. Download it and save as tests/fixtures/scanned_opinion.pdf
    3. Run: pytest tests/test_parser_edge_cases.py -v

If that fixture file is absent, TestScannedPDF is skipped automatically
rather than failing, so this file is still safe to run before you've
grabbed a fixture.

Run:
    pytest tests/test_parser_edge_cases.py -v
"""

import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from parser import extract_pages, chunk_pdf

SCANNED_FIXTURE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "fixtures", "scanned_opinion.pdf"
)


class TestCorruptedPDF:

    def test_garbage_bytes_raises_clear_exception(self, tmp_path):
        fake_pdf = tmp_path / "corrupted.pdf"
        fake_pdf.write_bytes(b"this is not a real PDF file, just garbage bytes \x00\x01\x02")

        # Must raise, not silently return [] or garbage chunks that would
        # flow downstream undetected.
        with pytest.raises(Exception):
            extract_pages(str(fake_pdf))

    def test_truncated_pdf_raises_clear_exception(self, tmp_path):
        # A PDF header with nothing valid after it -- simulates a download
        # that got cut off partway through.
        truncated = tmp_path / "truncated.pdf"
        truncated.write_bytes(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<< /Type")

        with pytest.raises(Exception):
            chunk_pdf(str(truncated))

    def test_nonexistent_file_raises_file_not_found_or_similar(self, tmp_path):
        missing = tmp_path / "does_not_exist.pdf"
        with pytest.raises(Exception):
            extract_pages(str(missing))

    def test_empty_file_does_not_silently_succeed(self, tmp_path):
        empty = tmp_path / "empty.pdf"
        empty.write_bytes(b"")
        with pytest.raises(Exception):
            extract_pages(str(empty))


@pytest.mark.skipif(
    not os.path.exists(SCANNED_FIXTURE_PATH),
    reason=(
        f"No scanned-PDF fixture at {SCANNED_FIXTURE_PATH}. "
        "Download a real scanned opinion from courtlistener.com to run this test."
    ),
)
class TestScannedPDF:

    def test_scanned_pdf_does_not_silently_produce_empty_chunks(self):
        chunks = chunk_pdf(SCANNED_FIXTURE_PATH)
        # A scanned/image-only PDF with no OCR layer will legitimately produce
        # zero chunks (PyMuPDF can't extract text from a raw image) -- that's
        # fine IF it's detectable. The real failure mode to catch is chunks
        # that look non-empty but are garbled/whitespace-only junk.
        for chunk in chunks:
            assert chunk["text"].strip(), "Found a chunk with only whitespace -- garbage output."

    def test_scanned_pdf_page_numbers_still_valid(self):
        chunks = chunk_pdf(SCANNED_FIXTURE_PATH)
        for chunk in chunks:
            assert isinstance(chunk["page_number"], int)
            assert chunk["page_number"] >= 1
