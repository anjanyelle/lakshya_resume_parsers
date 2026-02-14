from pathlib import Path

from app.services.parser import extract_text as extractor


def test_extract_pdf_triggers_ocr(monkeypatch, tmp_path):
    pdf_path = tmp_path / "resume.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n% test")

    class _Page:
        def extract_text(self):
            return ""

    class _PDF:
        pages = [_Page()]

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    class _ReaderPage:
        def extract_text(self):
            return ""

    class _Reader:
        pages = [_ReaderPage()]

    monkeypatch.setattr(extractor.pdfplumber, "open", lambda _: _PDF())
    monkeypatch.setattr(extractor, "PdfReader", lambda _: _Reader())
    monkeypatch.setattr(extractor, "_ocr_pdf", lambda _: ("OCR TEXT", 0.9))

    result = extractor._extract_pdf(pdf_path)
    assert result.used_ocr is True
    assert "OCR TEXT" in result.text
