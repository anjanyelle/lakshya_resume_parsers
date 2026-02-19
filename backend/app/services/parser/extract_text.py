from __future__ import annotations

from collections import Counter
import logging
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from pypdf import PdfReader
from docx import Document
from PIL import Image

from app.core.config import get_settings
from app.services.parser.normalize import normalize_resume_text, normalize_text

logger = logging.getLogger(__name__)


_MONTH_HINT_RE = re.compile(
    r"^(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ExtractedText:
    text: str
    ocr_confidence: float | None = None
    used_ocr: bool = False
    method: str = "unknown"


# ============================================================
# ENTRY POINT
# ============================================================

def extract_text(file_path: Path) -> ExtractedText:
    settings = get_settings()
    if settings.TESSERACT_CMD:
        pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

    extension = file_path.suffix.lower().lstrip(".")
    logger.info("Starting text extraction", extra={"path": str(file_path)})

    if extension == "pdf":
        return _extract_pdf(file_path)
    if extension == "docx":
        return _extract_docx(file_path)
    if extension == "doc":
        converted = _convert_doc_to_docx(file_path)
        return _extract_docx(converted)
    if extension in {"txt", "rtf"}:
        return _extract_plain_text(file_path, extension)
    if extension in {"png", "jpg", "jpeg"}:
        return _extract_image(file_path)

    raise ValueError(f"Unsupported file extension: {extension}")


# ============================================================
# HYBRID PDF STRATEGY
# ============================================================

def _extract_pdf(file_path: Path) -> ExtractedText:
    settings = get_settings()

    # ------------------------------------------------
    # STEP 1 — Try pypdf FIRST (preferred)
    # ------------------------------------------------
    text_pypdf = ""
    try:
        reader = PdfReader(str(file_path))
        text_pypdf = "\n".join(
            (page.extract_text() or "") for page in reader.pages
        ).strip()
    except Exception as exc:
        logger.warning("pypdf extraction failed", exc_info=exc)

    if _is_text_quality_good(text_pypdf):
        logger.info("Using pypdf extraction")
        return ExtractedText(
            text=normalize_resume_text(text_pypdf),
            method="pypdf",
        )

    # ------------------------------------------------
    # STEP 2 — Try pdfplumber (layout fallback)
    # ------------------------------------------------
    text_plumber = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            pages_lines: list[list[str]] = []
            for page in pdf.pages:
                raw = page.extract_text() or ""
                lines = [l.rstrip() for l in raw.splitlines() if l.strip()]
                pages_lines.append(lines)

        pages_lines = _strip_repeated_headers_footers(pages_lines)
        text_plumber = "\n\n".join(
            "\n".join(lines).strip() for lines in pages_lines
        ).strip()
    except Exception as exc:
        logger.warning("pdfplumber extraction failed", exc_info=exc)

    if _is_text_quality_good(text_plumber):
        logger.info("Using pdfplumber extraction")
        return ExtractedText(
            text=normalize_resume_text(text_plumber),
            method="pdfplumber",
        )

    # ------------------------------------------------
    # STEP 3 — OCR fallback
    # ------------------------------------------------
    logger.info("Falling back to OCR")
    ocr_text, ocr_conf = _ocr_pdf(file_path)

    return ExtractedText(
        text=normalize_resume_text(ocr_text),
        ocr_confidence=ocr_conf,
        used_ocr=True,
        method="ocr",
    )


# ============================================================
# QUALITY CHECK ENGINE
# ============================================================

def _is_text_quality_good(text: str) -> bool:
    if not text or len(text) < 200:
        return False

    # Too many merged long tokens
    long_tokens = [w for w in text.split() if len(w) > 30]
    if len(long_tokens) > 5:
        return False

    # Too many weird uppercase/lowercase merges
    if len(re.findall(r"[a-z][A-Z]", text)) > 20:
        return False

    # Too many artificial separators
    if text.count("|") > 10:
        return False

    # Too many abnormal long alpha runs
    if len(re.findall(r"[A-Za-z]{25,}", text)) > 5:
        return False

    return True


# ============================================================
# OCR
# ============================================================

def _extract_image(file_path: Path) -> ExtractedText:
    settings = get_settings()
    image = Image.open(str(file_path))

    data = pytesseract.image_to_data(
        image,
        lang=settings.TESSERACT_LANG,
        output_type=pytesseract.Output.DICT,
    )

    text = pytesseract.image_to_string(
        image,
        lang=settings.TESSERACT_LANG,
    ).strip()

    confidences: list[float] = []
    for conf in data.get("conf", []):
        try:
            conf_val = float(conf)
            if conf_val >= 0:
                confidences.append(conf_val)
        except Exception:
            continue

    avg_conf = sum(confidences) / len(confidences) if confidences else None

    return ExtractedText(
        text=normalize_text(text),
        ocr_confidence=avg_conf,
        used_ocr=True,
        method="ocr_image",
    )


def _ocr_pdf(file_path: Path) -> tuple[str, float | None]:
    settings = get_settings()
    images = convert_from_path(str(file_path), dpi=300)

    ocr_text_chunks: list[str] = []
    confidences: list[float] = []

    for image in images:
        data = pytesseract.image_to_data(
            image,
            lang=settings.TESSERACT_LANG,
            output_type=pytesseract.Output.DICT,
        )
        text = pytesseract.image_to_string(
            image,
            lang=settings.TESSERACT_LANG,
        ).strip()

        ocr_text_chunks.append(text)

        for conf in data.get("conf", []):
            try:
                conf_val = float(conf)
                if conf_val >= 0:
                    confidences.append(conf_val)
            except Exception:
                continue

    avg_conf = sum(confidences) / len(confidences) if confidences else None
    return "\n".join(ocr_text_chunks).strip(), avg_conf


# ============================================================
# DOCX
# ============================================================

def _extract_docx(file_path: Path) -> ExtractedText:
    document = Document(str(file_path))
    chunks: list[str] = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if text:
            chunks.append(text)

    for table in document.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            if any(cells):
                chunks.append(" | ".join(cells))

    text = "\n".join(chunks).strip()

    return ExtractedText(
        text=normalize_text(text),
        method="docx",
    )


# ============================================================
# PLAIN TEXT
# ============================================================

def _extract_plain_text(file_path: Path, extension: str) -> ExtractedText:
    raw = file_path.read_text(encoding="utf-8", errors="replace")
    return ExtractedText(
        text=normalize_text(raw),
        method=extension,
    )


# ============================================================
# DOC CONVERSION
# ============================================================

def _convert_doc_to_docx(file_path: Path) -> Path:
    output_dir = Path(tempfile.mkdtemp())

    subprocess.run(
        [
            "soffice",
            "--headless",
            "--convert-to",
            "docx",
            "--outdir",
            str(output_dir),
            str(file_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    converted = output_dir / f"{file_path.stem}.docx"

    if not converted.exists():
        raise RuntimeError("DOC conversion did not produce output")

    return converted


# ============================================================
# HEADER / FOOTER STRIPPER
# ============================================================

def _strip_repeated_headers_footers(pages_lines: list[list[str]]) -> list[list[str]]:
    if len(pages_lines) < 2:
        return pages_lines

    def norm(line: str) -> str:
        cleaned = re.sub(r"\s+", " ", line).strip().lower()
        cleaned = re.sub(r"\bpage\s*\d+\b", "", cleaned)
        cleaned = re.sub(r"\b\d+\b", "", cleaned)
        return cleaned.strip()

    header_candidates: list[str] = []
    footer_candidates: list[str] = []

    for lines in pages_lines:
        non_empty = [l for l in lines if l.strip()]
        header_candidates.extend(non_empty[:2])
        footer_candidates.extend(non_empty[-2:])

    header_counts = Counter(norm(l) for l in header_candidates if norm(l))
    footer_counts = Counter(norm(l) for l in footer_candidates if norm(l))

    page_count = len(pages_lines)

    header_remove = {
        k for k, v in header_counts.items()
        if v >= max(2, int(page_count * 0.6))
    }

    footer_remove = {
        k for k, v in footer_counts.items()
        if v >= max(2, int(page_count * 0.6))
    }

    cleaned_pages: list[list[str]] = []

    for lines in pages_lines:
        kept = []
        for line in lines:
            n = norm(line)
            if n in header_remove or n in footer_remove:
                continue
            kept.append(line)
        cleaned_pages.append(kept)

    return cleaned_pages
