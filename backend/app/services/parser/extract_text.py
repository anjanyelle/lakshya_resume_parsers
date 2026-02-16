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
    if extension in {"png", "jpg", "jpeg"}:
        return _extract_image(file_path)

    raise ValueError(f"Unsupported file extension: {extension}")


def _extract_image(file_path: Path) -> ExtractedText:
    settings = get_settings()
    image = Image.open(str(file_path))
    data = pytesseract.image_to_data(
        image, lang=settings.TESSERACT_LANG, output_type=pytesseract.Output.DICT
    )
    text = pytesseract.image_to_string(image, lang=settings.TESSERACT_LANG).strip()

    confidences: list[float] = []
    for conf in data.get("conf", []):
        try:
            conf_val = float(conf)
        except ValueError:
            continue
        if conf_val >= 0:
            confidences.append(conf_val)
    avg_conf = sum(confidences) / len(confidences) if confidences else None

    return ExtractedText(
        text=normalize_text(text),
        ocr_confidence=avg_conf,
        used_ocr=True,
        method="ocr_image",
    )


def _extract_pdf(file_path: Path) -> ExtractedText:
    settings = get_settings()
    text = ""
    method = "pdfplumber"

    try:
        with pdfplumber.open(file_path) as pdf:
            pages_lines: list[list[str]] = []
            for page in pdf.pages:
                lines = _extract_pdf_page_lines(page)
                pages_lines.append(lines)
        pages_lines = _strip_repeated_headers_footers(pages_lines)
        text = "\n\n".join("\n".join(lines).strip() for lines in pages_lines).strip()
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


def _extract_pdf_page_lines(page: object) -> list[str]:
    extract_words = getattr(page, "extract_words", None)
    if callable(extract_words):
        try:
            words = extract_words(
                keep_blank_chars=False,
                use_text_flow=True,
            )
        except TypeError:
            words = extract_words()
        except Exception:  # noqa: BLE001
            words = []

        if isinstance(words, list) and words:
            try:
                page_width = float(getattr(page, "width", 0.0) or 0.0)
            except Exception:  # noqa: BLE001
                page_width = 0.0
            return _reconstruct_lines_from_words(words, page_width)

    extract_text = getattr(page, "extract_text", None)
    if callable(extract_text):
        try:
            raw = extract_text() or ""
            return [line.rstrip() for line in raw.splitlines() if line.strip()]
        except Exception:  # noqa: BLE001
            return []
    return []


def _reconstruct_lines_from_words(words: list[dict], page_width: float) -> list[str]:
    cleaned_words: list[dict[str, object]] = []
    for w in words:
        if not isinstance(w, dict):
            continue
        text = str(w.get("text") or "").strip()
        if not text:
            continue
        try:
            x0 = float(w.get("x0") or 0.0)
            top = float(w.get("top") or 0.0)
        except Exception:  # noqa: BLE001
            continue
        cleaned_words.append({"text": text, "x0": x0, "top": top})

    if not cleaned_words:
        return []

    split_x = page_width * 0.5 if page_width else None
    two_column = False
    if split_x is not None and page_width > 0:
        left = sum(1 for w in cleaned_words if float(w["x0"]) < page_width * 0.4)
        right = sum(1 for w in cleaned_words if float(w["x0"]) > page_width * 0.6)
        total = len(cleaned_words)
        two_column = total > 0 and (left / total) > 0.15 and (right / total) > 0.15

    if two_column and split_x is not None:
        left_words = [w for w in cleaned_words if float(w["x0"]) < split_x]
        right_words = [w for w in cleaned_words if float(w["x0"]) >= split_x]
        left_lines = _group_words_into_lines(left_words)
        right_lines = _group_words_into_lines(right_words)
        return left_lines + ([""] if left_lines and right_lines else []) + right_lines

    return _group_words_into_lines(cleaned_words)


def _group_words_into_lines(words: list[dict[str, object]]) -> list[str]:
    if not words:
        return []

    words_sorted = sorted(words, key=lambda w: (float(w["top"]), float(w["x0"])))
    line_bins: list[list[dict[str, object]]] = []
    y_tol = 3.0
    for w in words_sorted:
        y = float(w["top"])
        if not line_bins:
            line_bins.append([w])
            continue
        last_y = float(line_bins[-1][0]["top"])
        if abs(y - last_y) <= y_tol:
            line_bins[-1].append(w)
        else:
            line_bins.append([w])

    lines: list[str] = []
    for bin_words in line_bins:
        sorted_words = sorted(bin_words, key=lambda w: float(w["x0"]))
        parts: list[str] = []
        last_x: float | None = None
        for w in sorted_words:
            token = str(w["text"])
            x = float(w["x0"])
            if last_x is not None and (x - last_x) >= 120:
                parts.append("|")
            parts.append(token)
            last_x = x
        line = " ".join(parts).strip()
        if line:
            lines.append(line)
    return lines


def _strip_repeated_headers_footers(pages_lines: list[list[str]]) -> list[list[str]]:
    if len(pages_lines) < 2:
        return pages_lines

    def norm(line: str) -> str:
        cleaned = re.sub(r"\s+", " ", line).strip().lower()
        cleaned = re.sub(r"\bpage\s*\d+\b", "", cleaned)
        cleaned = re.sub(r"\b\d+\s*/\s*\d+\b", "", cleaned)
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
        k
        for k, v in header_counts.items()
        if v >= max(2, int(page_count * 0.6)) and 0 < len(k) <= 80
    }
    footer_remove = {
        k
        for k, v in footer_counts.items()
        if v >= max(2, int(page_count * 0.6)) and 0 < len(k) <= 80
    }
    if not header_remove and not footer_remove:
        return pages_lines

    cleaned_pages: list[list[str]] = []
    for lines in pages_lines:
        kept: list[str] = []
        for line in lines:
            n = norm(line)
            if n in header_remove or n in footer_remove:
                continue
            kept.append(line)
        cleaned_pages.append(kept)
    return cleaned_pages


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
