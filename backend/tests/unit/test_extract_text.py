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


def test_reconstruct_two_column_layout_rowwise_merge_and_full_width_header():
    blocks = [
        extractor.LayoutBlock(x0=0, y0=0, x1=600, y1=20, text="JOHN DOE"),
        extractor.LayoutBlock(x0=0, y0=40, x1=280, y1=55, text="Left A"),
        extractor.LayoutBlock(x0=320, y0=40, x1=600, y1=55, text="Right A"),
        extractor.LayoutBlock(x0=0, y0=70, x1=280, y1=85, text="Left B"),
        extractor.LayoutBlock(x0=320, y0=70, x1=600, y1=85, text="Right B"),
    ]

    out = extractor.reconstruct_two_column_layout(blocks)
    lines = [ln for ln in out.splitlines() if ln.strip()]

    assert lines[0] == "JOHN DOE"
    assert lines[1] == "Left A | Right A"
    assert lines[2] == "Left B | Right B"


def test_reconstruct_two_column_layout_paragraph_break_punct_uppercase_and_bullets():
    blocks = [
        extractor.LayoutBlock(x0=0, y0=0, x1=600, y1=20, text="SUMMARY"),
        extractor.LayoutBlock(x0=0, y0=30, x1=600, y1=45, text="Built systems."),
        extractor.LayoutBlock(x0=0, y0=50, x1=600, y1=65, text="Led teams"),
        extractor.LayoutBlock(x0=0, y0=80, x1=600, y1=95, text="- First bullet."),
        extractor.LayoutBlock(x0=0, y0=100, x1=600, y1=115, text="- Second bullet"),
    ]

    out = extractor.reconstruct_two_column_layout(blocks)
    lines = out.splitlines()

    # Punctuation-ending followed by uppercase-starting should create a blank line.
    idx = lines.index("Built systems.")
    assert lines[idx + 1] == ""
    assert lines[idx + 2] == "Led teams"

    # Bullet list should not be split into extra paragraphs due to punctuation.
    assert "- First bullet." in lines
    assert "- Second bullet" in lines
