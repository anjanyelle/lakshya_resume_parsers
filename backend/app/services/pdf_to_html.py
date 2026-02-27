"""Convert PDF to HTML for resume preview with click-to-highlight support."""

from __future__ import annotations

import html
import logging
from pathlib import Path

from app.core.config import get_settings
from app.services.parser.extract_text import extract_text

logger = logging.getLogger(__name__)

try:
    import fitz  # PyMuPDF

    HAS_FITZ = True
except ImportError:
    fitz = None  # type: ignore
    HAS_FITZ = False


def pdf_to_html(file_path: Path, page_limit: int | None = None) -> str:
    """
    Convert PDF to HTML for display in the resume viewer.
    Uses PyMuPDF for layout-preserving HTML when available;
    falls back to extracted text wrapped in <p> tags.
    """
    ext = file_path.suffix.lower().lstrip(".")
    if ext != "pdf":
        raise ValueError(f"Expected PDF, got {ext}")

    limit = page_limit or getattr(get_settings(), "PDF_MAX_PAGES", 50)

    if HAS_FITZ and fitz is not None:
        try:
            return _pdf_to_html_pymupdf(file_path, page_limit=limit)
        except Exception as exc:
            logger.warning("PyMuPDF PDF-to-HTML failed, using text fallback: %s", exc)

    return _pdf_to_html_from_text(file_path, page_limit=limit)


def _pdf_to_html_pymupdf(file_path: Path, page_limit: int) -> str:
    """Convert PDF to HTML using PyMuPDF's built-in HTML export."""
    doc = fitz.open(str(file_path))
    parts: list[str] = []
    try:
        for i in range(min(len(doc), page_limit)):
            page = doc.load_page(i)
            html_fragment = page.get_text("html")
            if html_fragment and html_fragment.strip():
                parts.append(html_fragment.strip())
    finally:
        doc.close()

    if not parts:
        return "<p>No content extracted.</p>"

    body = "\n".join(parts)
    return f'<div class="pdf-html-content">{body}</div>'


def _pdf_to_html_from_text(file_path: Path, page_limit: int) -> str:
    """Fallback: extract text and wrap in HTML paragraphs."""
    _ = page_limit  # extract_text uses settings.PDF_MAX_PAGES
    extracted = extract_text(file_path)
    text = extracted.text or ""
    if not text.strip():
        return "<p>No content extracted.</p>"

    paragraphs: list[str] = []
    for block in text.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        escaped = html.escape(block)
        if block.startswith("- ") or block.startswith("• "):
            paragraphs.append(f"<li>{escaped[2:]}</li>")
        elif block.startswith("## "):
            paragraphs.append(f"<h2>{escaped[3:]}</h2>")
        else:
            paragraphs.append(f"<p>{escaped}</p>")

    if not paragraphs:
        return "<p>No content extracted.</p>"

    html_content = "\n".join(paragraphs)
    return f'<div class="pdf-html-content prose prose-slate max-w-none">{html_content}</div>'
