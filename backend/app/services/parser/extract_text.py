from __future__ import annotations

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

from app.core.config import get_settings
from app.services.parser.normalize import normalize_text

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ExtractedText:
    text: str
    ocr_confidence: float | None = None
    used_ocr: bool = False
    method: str = "unknown"


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

    raise ValueError(f"Unsupported file extension: {extension}")


def _extract_pdf(file_path: Path) -> ExtractedText:
    settings = get_settings()
    text = ""
    method = "pdfplumber"

    try:
        with pdfplumber.open(file_path) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        text = "\n".join(pages).strip()
    except Exception as exc:  # noqa: BLE001
        logger.warning("pdfplumber failed, falling back to pypdf", exc_info=exc)

    if len(text) < settings.OCR_MIN_TEXT_CHARS:
        try:
            reader = PdfReader(str(file_path))
            fallback_text = "\n".join(
                (page.extract_text() or "") for page in reader.pages
            ).strip()
            if len(fallback_text) > len(text):
                text = fallback_text
                method = "pypdf"
        except Exception as exc:  # noqa: BLE001
            logger.warning("pypdf fallback failed", exc_info=exc)

    if len(text) < settings.OCR_MIN_TEXT_CHARS:
        logger.info("Low text detected, triggering OCR")
        ocr_text, ocr_conf = _ocr_pdf(file_path)
        return ExtractedText(
            text=normalize_text(ocr_text),
            ocr_confidence=ocr_conf,
            used_ocr=True,
            method="ocr",
        )

    return ExtractedText(text=normalize_text(text), method=method)


def _ocr_pdf(file_path: Path) -> tuple[str, float | None]:
    settings = get_settings()
    images = convert_from_path(str(file_path), dpi=300)
    ocr_text_chunks: list[str] = []
    confidences: list[float] = []

    for image in images:
        data = pytesseract.image_to_data(
            image, lang=settings.TESSERACT_LANG, output_type=pytesseract.Output.DICT
        )
        text = pytesseract.image_to_string(
            image, lang=settings.TESSERACT_LANG
        ).strip()
        ocr_text_chunks.append(text)

        for conf in data.get("conf", []):
            try:
                conf_val = float(conf)
            except ValueError:
                continue
            if conf_val >= 0:
                confidences.append(conf_val)

    avg_conf = sum(confidences) / len(confidences) if confidences else None
    return "\n".join(ocr_text_chunks).strip(), avg_conf


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
    return ExtractedText(text=normalize_text(text), method="docx")


def _extract_plain_text(file_path: Path, extension: str) -> ExtractedText:
    raw = file_path.read_text(encoding="utf-8", errors="replace")
    if extension == "rtf":
        raw = _strip_rtf(raw)
    return ExtractedText(text=normalize_text(raw), method=extension)


def _strip_rtf(text: str) -> str:
    # Decode hex-encoded characters like \'e9
    def _hex_replace(match: re.Match[str]) -> str:
        hex_value = match.group(1)
        try:
            return bytes.fromhex(hex_value).decode("latin-1")
        except ValueError:
            return ""

    text = re.sub(r"\\'([0-9a-fA-F]{2})", _hex_replace, text)
    text = re.sub(r"\\par[d]?", "\n", text)
    text = re.sub(r"\\[a-zA-Z]+\d* ?", "", text)
    text = text.replace("{", "").replace("}", "")
    return text


def _convert_doc_to_docx(file_path: Path) -> Path:
    output_dir = Path(tempfile.mkdtemp())
    try:
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
    except subprocess.CalledProcessError as exc:
        logger.exception("DOC to DOCX conversion failed", extra={"stderr": exc.stderr})
        raise RuntimeError("DOC conversion failed") from exc

    converted = output_dir / f"{file_path.stem}.docx"
    if not converted.exists():
        raise RuntimeError("DOC conversion did not produce output")
    return converted
