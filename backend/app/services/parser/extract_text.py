from __future__ import annotations

from collections import Counter
import logging
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from statistics import median

try:
    import fitz  # PyMuPDF
    HAS_FITZ = True
except ImportError:
    fitz = None  # type: ignore
    HAS_FITZ = False

import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from pypdf import PdfReader
from docx import Document
from docx.oxml.ns import qn
from PIL import Image

from app.core.config import get_settings
from app.core.observability import OCR_TRIGGER_TOTAL
from app.services.parser.normalize import normalize_resume_text, normalize_text

logger = logging.getLogger(__name__)

_OCR_LANG_MAP = {"hi": "hin", "ar": "ara", "zh-cn": "chi_sim", "zh": "chi_sim"}


_MONTH_HINT_RE = re.compile(
    r"^(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)\b",
    re.IGNORECASE,
)


_BULLET_PREFIX_RE = re.compile(
    r"^(\s*)(?:[\-\*•●○\u2022\u2023\u25E6\u25CF\u25CB\u2043\u2219\uf0b7\uf0a7\uf0d8\uf0fc▪·–—])\s+"
)


@dataclass(frozen=True)
class ExtractedText:
    text: str
    ocr_confidence: float | None = None
    used_ocr: bool = False
    method: str = "unknown"
    debug: dict[str, object] | None = None


@dataclass(frozen=True)
class LayoutBlock:
    x0: float
    y0: float
    x1: float
    y1: float
    text: str

    @property
    def x_center(self) -> float:
        return (self.x0 + self.x1) * 0.5

    @property
    def width(self) -> float:
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        return self.y1 - self.y0


def _normalize_bullet_prefix(line: str) -> str:
    if not line:
        return line
    return _BULLET_PREFIX_RE.sub(r"\1- ", line)


def _normalize_bullets_in_pages(pages_lines: list[list[str]]) -> list[list[str]]:
    out: list[list[str]] = []
    for lines in pages_lines:
        out.append([_normalize_bullet_prefix(ln) for ln in lines])
    return out


def _page_boundaries_from_pages_lines(pages_lines: list[list[str]]) -> list[dict[str, int]]:
    boundaries: list[dict[str, int]] = []
    line_cursor = 1
    for i, lines in enumerate(pages_lines):
        start_line = line_cursor
        line_cursor += len(lines)
        end_line = line_cursor - 1 if lines else start_line - 1
        boundaries.append(
            {
                "page_index": i,
                "start_line": start_line,
                "end_line": end_line,
                "line_count": len(lines),
            }
        )
        if i < (len(pages_lines) - 1):
            line_cursor += 1
    return boundaries


def _blocks_to_text(blocks: list[LayoutBlock]) -> str:
    """Convert blocks sorted by y to text lines."""
    lines = [b.text.strip() for b in sorted(blocks, key=lambda b: b.y0) if b.text.strip()]
    return "\n".join(lines)


def reconstruct_multicolumn_layout(
    blocks: list[LayoutBlock],
    page_width: float | None = None,
) -> str:
    """Detect 1, 2, or 3+ columns from block x-positions and merge column-major."""
    if not blocks:
        return ""

    min_x0 = min(b.x0 for b in blocks)
    max_x1 = max(b.x1 for b in blocks)
    pw = page_width if page_width is not None else max(1.0, max_x1 - min_x0)

    xs = sorted(set(round((b.x0 - min_x0) / 50) * 50 for b in blocks))
    col_starts = [0.0]
    for i in range(1, len(xs)):
        if xs[i] - xs[i - 1] > 60:
            col_starts.append(xs[i])
    col_starts.append(pw)
    n_cols = len(col_starts) - 1

    if n_cols == 1:
        return _blocks_to_text(blocks)

    columns: list[list[LayoutBlock]] = [[] for _ in range(n_cols)]
    for b in blocks:
        rel_x = b.x0 - min_x0
        assigned = False
        for i in range(n_cols):
            if col_starts[i] <= rel_x < col_starts[i + 1]:
                columns[i].append(b)
                assigned = True
                break
        if not assigned:
            columns[-1].append(b)

    parts = [_blocks_to_text(col) for col in columns]
    return "\n\n".join(p for p in parts if p)


def reconstruct_two_column_layout(blocks: list[LayoutBlock]) -> str:
    """Thin wrapper for backward compatibility; delegates to reconstruct_multicolumn_layout."""
    return reconstruct_multicolumn_layout(blocks)


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
# QUALITY CHECK ENGINE (used by first PDF path if present)
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
    if settings.TESSERACT_CMD:
        pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
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


def _extract_pdf(file_path: Path) -> ExtractedText:
    settings = get_settings()
    text = ""
    method = "pdfplumber"
    debug: dict[str, object] = {}

    try:
        pymupdf_text = extract_text_from_pdf_pymupdf_layout(file_path, debug=debug)
        if len(pymupdf_text) >= settings.OCR_MIN_TEXT_CHARS:
            text = pymupdf_text
            method = "pymupdf"
            debug["pymupdf_layout"] = True
    except Exception as exc:  # noqa: BLE001
        logger.info("PyMuPDF extraction unavailable", exc_info=exc)

    if not text:
        try:
            with pdfplumber.open(file_path) as pdf:
                pages_lines: list[list[str]] = []
                pages_columns: list[int] = []
                total_nonempty_lines = 0
                for page in pdf.pages:
                    lines, meta = _extract_pdf_page_lines_pdfplumber(page)
                    pages_lines.append(lines)
                    try:
                        cols = int(meta.get("detected_columns", 1)) if isinstance(meta, dict) else 1
                    except Exception:  # noqa: BLE001
                        cols = 1
                    pages_columns.append(cols)
                    total_nonempty_lines += sum(1 for ln in lines if ln.strip())
                debug["pdf_pages_sample"] = [lines[:40] for lines in pages_lines[:2]]
                debug["pdfplumber"] = {
                    "detected_columns": pages_columns[:10],
                    "line_count": int(total_nonempty_lines),
                }
            pages_lines = _strip_repeated_headers_footers(pages_lines)
            pages_lines = _normalize_bullets_in_pages(pages_lines)
            debug["pdfplumber_page_boundaries"] = _page_boundaries_from_pages_lines(pages_lines)
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
        OCR_TRIGGER_TOTAL.inc()
        try:
            ocr_text, ocr_conf, ocr_metadata = _ocr_pdf(file_path)
            merged_debug = {**(debug or {}), **(ocr_metadata or {})}
            return ExtractedText(
                text=normalize_resume_text(ocr_text, source_format="ocr"),
                ocr_confidence=ocr_conf,
                used_ocr=True,
                method="ocr",
                debug=merged_debug if merged_debug else None,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("OCR failed; returning best-effort extracted text", exc_info=exc)
            debug["ocr_failed"] = True
            debug["ocr_error"] = str(exc)

    source_fmt = "ocr" if method == "ocr" else "pdf"
    return ExtractedText(
        text=normalize_resume_text(text, source_format=source_fmt),
        method=method,
        debug=debug or None,
    )


def _extract_pdf_pymupdf_blocks(file_path: Path) -> str:
    if not HAS_FITZ or fitz is None:
        raise ImportError("PyMuPDF (pymupdf) is required for layout-aware PDF extraction. Install with: poetry add pymupdf")

    doc = fitz.open(str(file_path))
    blocks_out: list[str] = []
    try:
        for page in doc:
            page_blocks: list[tuple[float, float, str]] = []
            for block in page.get_text("blocks"):
                if not isinstance(block, (list, tuple)) or len(block) < 5:
                    continue
                x0, y0, x1, y1, text = block[:5]
                if not isinstance(text, str):
                    continue
                cleaned = "\n".join(
                    line.rstrip() for line in text.splitlines() if line.strip()
                ).strip()
                if not cleaned:
                    continue
                try:
                    page_blocks.append((float(y0), float(x0), cleaned))
                except Exception:  # noqa: BLE001
                    continue

            page_blocks.sort(key=lambda item: (item[0], item[1]))
            if page_blocks:
                blocks_out.append("\n".join([b[2] for b in page_blocks]).strip())
    finally:
        doc.close()

    return "\n\n".join([b for b in blocks_out if b]).strip()


def extract_text_from_pdf_pymupdf_layout(
    file_path: Path,
    *,
    debug: dict[str, object] | None = None,
) -> str:
    if not HAS_FITZ or fitz is None:
        raise ImportError("PyMuPDF (pymupdf) is required for layout-aware PDF extraction. Install with: poetry add pymupdf")

    def _clean_fragment(value: str) -> str:
        cleaned = "\n".join(line.rstrip() for line in value.splitlines() if line.strip())
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    doc = fitz.open(str(file_path))
    pages_out: list[str] = []
    try:
        for page in doc:
            page_dict = page.get_text("dict")
            items: list[LayoutBlock] = []
            for block in page_dict.get("blocks", []) if isinstance(page_dict, dict) else []:
                if not isinstance(block, dict):
                    continue
                for line in block.get("lines", []) or []:
                    if not isinstance(line, dict):
                        continue
                    bbox = line.get("bbox")
                    if not (isinstance(bbox, (list, tuple)) and len(bbox) == 4):
                        continue
                    try:
                        x0, y0, x1, y1 = (float(b) for b in bbox)
                    except Exception:  # noqa: BLE001
                        continue

                    spans = line.get("spans", []) or []
                    if not isinstance(spans, list):
                        continue
                    raw = "".join(str(span.get("text") or "") for span in spans if isinstance(span, dict))
                    cleaned = _normalize_bullet_prefix(_clean_fragment(raw))
                    if not cleaned:
                        continue
                    items.append(LayoutBlock(x0=x0, y0=y0, x1=x1, y1=y1, text=cleaned))

            if not items:
                page_text = _clean_fragment(page.get_text("text") or "")
                if page_text:
                    pages_out.append(page_text)
                continue

            page_out = reconstruct_multicolumn_layout(items).strip()
            if page_out:
                pages_out.append(page_out)
    finally:
        doc.close()

    pages_lines: list[list[str]] = []
    for p in pages_out:
        pages_lines.append(p.split("\n"))
    pages_lines = _strip_repeated_headers_footers(pages_lines)
    pages_lines = _normalize_bullets_in_pages(pages_lines)
    if debug is not None:
        debug["pymupdf_page_boundaries"] = _page_boundaries_from_pages_lines(pages_lines)
    return "\n\n".join("\n".join(lines).strip() for lines in pages_lines).strip()


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
            lines, _ = _reconstruct_lines_from_words_with_layout(words, page_width)
            return lines

    extract_text = getattr(page, "extract_text", None)
    if callable(extract_text):
        try:
            raw = extract_text() or ""
            return [line.rstrip() for line in raw.splitlines() if line.strip()]
        except Exception:  # noqa: BLE001
            return []


def _in_bbox(word: dict, bbox: tuple[float, float, float, float]) -> bool:
    x0, y0, x1, y1 = bbox
    return (
        x0 <= word.get("x0", 0)
        and word.get("x1", 0) <= x1
        and y0 <= word.get("top", 0)
        and word.get("bottom", 0) <= y1
    )


def _extract_page_with_tables(page: object) -> tuple[list[str], dict[str, object]]:
    lines: list[str] = []
    extract_tables = getattr(page, "extract_tables", None)
    find_tables = getattr(page, "find_tables", None)
    if callable(extract_tables):
        try:
            for table in extract_tables() or []:
                if not table:
                    continue
                for row in table:
                    cells = [str(c or "").strip() for c in row]
                    cells = [c for c in cells if c]
                    if cells:
                        lines.append(" | ".join(cells))
        except Exception:  # noqa: BLE001
            pass
    table_bboxes: list[tuple[float, float, float, float]] = []
    if callable(find_tables):
        try:
            for t in find_tables() or []:
                bbox = getattr(t, "bbox", None)
                if bbox and len(bbox) >= 4:
                    table_bboxes.append(tuple(bbox[:4]))
        except Exception:  # noqa: BLE001
            pass
    extract_words = getattr(page, "extract_words", None)
    if callable(extract_words):
        try:
            words = extract_words(keep_blank_chars=False, use_text_flow=True)
        except TypeError:
            words = extract_words()
        except Exception:  # noqa: BLE001
            words = []
        if isinstance(words, list) and words:
            try:
                non_table_words = [
                    w for w in words
                    if not any(_in_bbox(w, b) for b in table_bboxes)
                ]
                if non_table_words:
                    try:
                        page_width = float(getattr(page, "width", 0.0) or 0.0)
                    except Exception:  # noqa: BLE001
                        page_width = 0.0
                    extra_lines, _ = _reconstruct_lines_from_words_with_layout(
                        non_table_words, page_width
                    )
                    lines.extend(extra_lines)
            except Exception:  # noqa: BLE001
                pass
    elif not lines:
        extract_text = getattr(page, "extract_text", None)
        if callable(extract_text):
            try:
                raw = extract_text() or ""
                lines = [ln.rstrip() for ln in raw.splitlines() if ln.strip()]
            except Exception:  # noqa: BLE001
                pass
    return lines, {"detected_columns": 1, "line_count": len(lines)}


def _extract_pdf_page_lines_pdfplumber(page: object) -> tuple[list[str], dict[str, object]]:
    try:
        lines, meta = _extract_page_with_tables(page)
        if lines:
            return lines, meta
    except Exception:  # noqa: BLE001
        pass
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
            lines, meta = _reconstruct_lines_from_words_with_layout(words, page_width)
            return lines, meta

    extract_text = getattr(page, "extract_text", None)
    if callable(extract_text):
        try:
            raw = extract_text() or ""
            lines = [line.rstrip() for line in raw.splitlines() if line.strip()]
            return lines, {"detected_columns": 1, "line_count": len(lines)}
        except Exception:  # noqa: BLE001
            return [], {"detected_columns": 1, "line_count": 0}
    return [], {"detected_columns": 1, "line_count": 0}


def _reconstruct_lines_from_words(words: list[dict], page_width: float) -> list[str]:
    lines, _ = _reconstruct_lines_from_words_with_layout(words, page_width)
    return lines


def _reconstruct_lines_from_words_with_layout(
    words: list[dict],
    page_width: float,
) -> tuple[list[str], dict[str, object]]:
    cleaned_words: list[dict[str, object]] = []
    heights: list[float] = []
    for w in words:
        if not isinstance(w, dict):
            continue
        text = str(w.get("text") or "").strip()
        if not text:
            continue
        try:
            x0 = float(w.get("x0") or 0.0)
            x1 = float(w.get("x1") or 0.0)
            top = float(w.get("top") or 0.0)
            bottom = float(w.get("bottom") or top)
        except Exception:  # noqa: BLE001
            continue
        cleaned_words.append({"text": text, "x0": x0, "x1": x1, "top": top, "bottom": bottom})
        h = bottom - top
        if h > 0:
            heights.append(h)

    if not cleaned_words:
        return [], {"detected_columns": 1, "line_count": 0}

    typical_h = median(heights) if heights else 10.0
    y_tol = max(2.5, typical_h * 0.35)

    def _is_bullet_line(value: str) -> bool:
        cleaned = (value or "").lstrip()
        if not cleaned:
            return False
        if cleaned.startswith(("-", "•", "*", "·", "▪", "–")):
            return True
        return bool(re.match(r"^\d{1,2}\s*[\.)]\s+", cleaned))

    def _starts_upper(value: str) -> bool:
        cleaned = (value or "").lstrip()
        return bool(re.match(r"^[A-Z]", cleaned))

    gap_threshold = 120.0
    if page_width and page_width > 0:
        gap_threshold = max(60.0, float(page_width) * 0.12)

    ws_sorted = sorted(cleaned_words, key=lambda w: (float(w["top"]), float(w["x0"])))
    line_bins: list[dict[str, object]] = []
    for w in ws_sorted:
        y0 = float(w["top"])
        y1 = float(w["bottom"])
        if not line_bins:
            line_bins.append({"y0": y0, "y1": y1, "words": [w]})
            continue
        last = line_bins[-1]
        by0 = float(last["y0"])
        by1 = float(last["y1"])
        overlap = min(y1, by1) - max(y0, by0)
        if overlap >= 0.0 or abs(y0 - by0) <= y_tol:
            last["y0"] = min(by0, y0)
            last["y1"] = max(by1, y1)
            cast_words = last["words"]
            if isinstance(cast_words, list):
                cast_words.append(w)
        else:
            line_bins.append({"y0": y0, "y1": y1, "words": [w]})

    blocks: list[LayoutBlock] = []
    for b in line_bins:
        b_words = b.get("words", [])
        if not isinstance(b_words, list) or not b_words:
            continue
        sorted_words = sorted(b_words, key=lambda ww: float(ww["x0"]))
        parts: list[str] = []
        last_x1: float | None = None
        min_x0 = float("inf")
        max_x1 = 0.0
        for ww in sorted_words:
            token = str(ww.get("text") or "")
            if not token:
                continue
            x0 = float(ww.get("x0") or 0.0)
            x1 = float(ww.get("x1") or x0)
            min_x0 = min(min_x0, x0)
            max_x1 = max(max_x1, x1)
            if last_x1 is not None and (x0 - last_x1) >= gap_threshold:
                parts.append("|")
            parts.append(token)
            last_x1 = x1
        line = " ".join(parts).strip()
        if not line or min_x0 == float("inf"):
            continue
        blocks.append(
            LayoutBlock(
                x0=float(min_x0),
                y0=float(b["y0"]),
                x1=float(max_x1),
                y1=float(b["y1"]),
                text=_normalize_bullet_prefix(line),
            )
        )

    if not blocks:
        return [], {"detected_columns": 1, "line_count": 0}

    layout_text = reconstruct_multicolumn_layout(blocks).strip()
    out_lines = [ln for ln in layout_text.split("\n")]
    nonempty = sum(1 for ln in out_lines if ln.strip())

    detected_columns = 1
    if page_width and page_width > 0:
        min_x0b = min(b.x0 for b in blocks)
        max_x1b = max(b.x1 for b in blocks)
        page_w = max(1.0, max_x1b - min_x0b)
        midpoint = min_x0b + (page_w * 0.5)
        full_width = [b for b in blocks if b.width >= (page_w * 0.85)]
        non_full = [b for b in blocks if b not in full_width]
        left = [b for b in non_full if b.x_center < midpoint]
        right = [b for b in non_full if b.x_center >= midpoint]
        if left and right:
            detected_columns = 2

    return out_lines, {"detected_columns": detected_columns, "line_count": int(nonempty)}


def _group_words_into_lines(
    words: list[dict[str, object]],
    *,
    gap_threshold: float = 120.0,
) -> list[str]:
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
            if last_x is not None and (x - last_x) >= gap_threshold:
                parts.append("|")
            parts.append(token)
            last_x = x
        line = " ".join(parts).strip()
        if line:
            lines.append(line)
    return lines


def _strip_repeated_headers_footers(pages_lines: list[list[str]]) -> list[list[str]]:
    """Remove repeated headers/footers and industry-style page markers (e.g. '-- 1 of 10 --')."""
    if len(pages_lines) < 2:
        return pages_lines

    # Enterprise: strip page markers like "-- 1 of 10 --" and standalone page numbers
    _PAGE_MARKER_RE = re.compile(r"^\s*--\s*\d+\s+of\s+\d+\s*--\s*$", re.IGNORECASE)
    _STANDALONE_DIGIT_RE = re.compile(r"^\s*\d{1,3}\s*$")

    def _drop_page_markers(lines: list[str]) -> list[str]:
        out: list[str] = []
        for i, line in enumerate(lines):
            if _PAGE_MARKER_RE.match(line.strip()):
                continue
            if _STANDALONE_DIGIT_RE.match(line.strip()) and (i < 2 or i >= max(0, len(lines) - 2)):
                continue
            out.append(line)
        return out

    pages_lines = [_drop_page_markers(p) for p in pages_lines]

    def norm(line: str) -> str:
        cleaned = re.sub(r"\s+", " ", line).strip().lower()
        cleaned = re.sub(r"\bpage\s*\d+\b", "", cleaned)
        cleaned = re.sub(r"\b\d+\s*/\s*\d+\b", "", cleaned)
        cleaned = re.sub(r"\b\d+\b", "", cleaned)
        return cleaned.strip()

    heading_re = re.compile(
        r"^(experience|work\s*experience|professional\s*experience|education|skills|projects|summary|certifications?)$",
        re.IGNORECASE,
    )

    header_candidates: list[str] = []
    footer_candidates: list[str] = []
    for lines in pages_lines:
        non_empty = [l for l in lines if l.strip()]
        header_candidates.extend(non_empty[:3])
        footer_candidates.extend(non_empty[-3:])

    header_counts = Counter(
        norm(l)
        for l in header_candidates
        if norm(l) and not heading_re.match(norm(l))
    )
    footer_counts = Counter(
        norm(l)
        for l in footer_candidates
        if norm(l) and not heading_re.match(norm(l))
    )
    page_count = len(pages_lines)
    header_remove = {
        k
        for k, v in header_counts.items()
        if v >= max(2, int(page_count * 0.55)) and 0 < len(k) <= 100
    }
    footer_remove = {
        k
        for k, v in footer_counts.items()
        if v >= max(2, int(page_count * 0.55)) and 0 < len(k) <= 100
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


def _ocr_pdf(file_path: Path) -> tuple[str, float | None, dict[str, object] | None]:
    settings = get_settings()
    if settings.TESSERACT_CMD:
        pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
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
    full_text = "\n".join(ocr_text_chunks).strip()

    if avg_conf is not None and avg_conf < 60:
        images_400 = convert_from_path(str(file_path), dpi=400)
        ocr_text_chunks = []
        confidences = []
        for image in images_400:
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
        new_avg = sum(confidences) / len(confidences) if confidences else avg_conf
        if new_avg > avg_conf:
            full_text = "\n".join(ocr_text_chunks).strip()
            avg_conf = new_avg

    metadata: dict[str, object] | None = None
    if avg_conf is not None and avg_conf < 40:
        logger.warning("Low OCR confidence %.0f%% — flagging for review", avg_conf)
        metadata = {"ocr_confidence": avg_conf, "needs_review": True}
    return full_text, avg_conf, metadata


# ============================================================
# DOCX
# ============================================================

def _extract_docx(file_path: Path) -> ExtractedText:
    document = Document(str(file_path))

    def _style_name(paragraph: object) -> str:
        style = getattr(paragraph, "style", None)
        name = getattr(style, "name", "") if style is not None else ""
        return str(name or "")

    def _is_list_paragraph(paragraph: object) -> bool:
        try:
            p = getattr(paragraph, "_p", None)
            if p is None:
                return False
            pPr = p.find(qn("w:pPr"))
            if pPr is None:
                return False
            numPr = pPr.find(qn("w:numPr"))
            if numPr is not None:
                return True
            ind = pPr.find(qn("w:ind"))
            if ind is not None:
                left_val = ind.get(qn("w:left"))
                if left_val is not None:
                    try:
                        if int(left_val) >= 360:
                            return True
                    except (TypeError, ValueError):
                        pass
        except Exception:  # noqa: BLE001
            pass
        name = _style_name(paragraph)
        return "list" in name.lower()

    def _is_heading_paragraph(paragraph: object) -> bool:
        style_name = _style_name(paragraph).lower()
        if style_name.startswith("heading"):
            return True
        heading_keywords = ("heading", "header", "section", "title")
        if any(kw in style_name for kw in heading_keywords):
            return True
        text = str(getattr(paragraph, "text", "") or "").strip()
        if not text or len(text.split()) >= 6:
            return False
        if not text.isupper() or not any(c.isalpha() for c in text):
            return False
        runs = getattr(paragraph, "runs", []) or []
        if not runs:
            return False
        bold_runs = [r for r in runs if getattr(getattr(r, "font", None), "bold", None) is True]
        return len(bold_runs) >= 1 and len("".join(str(getattr(r, "text", "") or "") for r in bold_runs).strip()) > 0

    def _emit_paragraph_text(paragraph: object) -> str:
        text = str(getattr(paragraph, "text", "") or "").strip()
        if not text:
            return ""
        if _is_heading_paragraph(paragraph):
            return f"## {text}"
        if _is_list_paragraph(paragraph):
            return f"- {text}"
        return text

    def _emit_paragraph_lines(paragraph: object) -> list[str]:
        line = _emit_paragraph_text(paragraph)
        return [line] if line else []

    def _cell_lines(cell: object) -> list[str]:
        lines: list[str] = []
        paragraphs = getattr(cell, "paragraphs", [])
        if isinstance(paragraphs, list):
            for p in paragraphs:
                lines.extend(_emit_paragraph_lines(p))
        return [ln for ln in lines if ln.strip()]

    def _looks_like_data_table(table: object) -> bool:
        rows = getattr(table, "rows", [])
        if not isinstance(rows, list) or not rows:
            return False
        if len(rows) < 2:
            return False
        try:
            max_cols = max(len(getattr(r, "cells", []) or []) for r in rows)
        except Exception:  # noqa: BLE001
            return False
        if max_cols < 2:
            return False

        non_empty_cells_per_row: list[int] = []
        for r in rows[:12]:
            cells = getattr(r, "cells", [])
            if not isinstance(cells, list) or not cells:
                continue
            count = 0
            for c in cells:
                value = " ".join(_cell_lines(c)).strip()
                if value:
                    count += 1
            non_empty_cells_per_row.append(count)

        if not non_empty_cells_per_row:
            return False

        avg_non_empty = sum(non_empty_cells_per_row) / max(1, len(non_empty_cells_per_row))
        if avg_non_empty < 1.7:
            return False

        return True

    def _table_to_lines(table: object) -> list[str]:
        out_lines: list[str] = []
        rows = getattr(table, "rows", [])
        if not isinstance(rows, list) or not rows:
            return out_lines

        is_data_table = _looks_like_data_table(table)

        for row in rows:
            cells = getattr(row, "cells", [])
            if not isinstance(cells, list) or not cells:
                continue

            if is_data_table:
                rendered_cells: list[str] = []
                for cell in cells:
                    cell_text = " ".join(_cell_lines(cell)).strip()
                    rendered_cells.append(cell_text)
                if any(c.strip() for c in rendered_cells):
                    out_lines.append(" | ".join(c.strip() for c in rendered_cells))
            else:
                for cell in cells:
                    cell_block = _cell_lines(cell)
                    if cell_block:
                        out_lines.extend(cell_block)
                        out_lines.append("")

        while out_lines and not out_lines[-1].strip():
            out_lines.pop()
        return out_lines

    def _extract_headers_footers() -> tuple[str, str]:
        header_lines: list[str] = []
        footer_lines: list[str] = []
        for section in getattr(document, "sections", []):
            header = getattr(section, "header", None)
            footer = getattr(section, "footer", None)
            if header is not None:
                for p in getattr(header, "paragraphs", []) or []:
                    header_lines.extend(_emit_paragraph_lines(p))
            if footer is not None:
                for p in getattr(footer, "paragraphs", []) or []:
                    footer_lines.extend(_emit_paragraph_lines(p))

        header_text = "\n".join([ln for ln in header_lines if ln.strip()]).strip()
        footer_text = "\n".join([ln for ln in footer_lines if ln.strip()]).strip()
        return header_text, footer_text

    def _extract_textboxes() -> list[list[str]]:
        try:
            from docx.oxml.ns import nsmap  # type: ignore
        except Exception:  # noqa: BLE001
            return []

        blocks: list[list[str]] = []
        try:
            txbx_nodes = document.element.body.xpath(
                ".//w:txbxContent",
                namespaces=nsmap,
            )
        except Exception:  # noqa: BLE001
            return []

        for node in txbx_nodes or []:
            lines: list[str] = []
            try:
                paragraphs = node.xpath(".//w:p", namespaces=nsmap)
            except Exception:  # noqa: BLE001
                paragraphs = []
            for p in paragraphs or []:
                try:
                    texts = p.xpath(".//w:t", namespaces=nsmap)
                except Exception:  # noqa: BLE001
                    texts = []
                line = "".join((t.text or "") for t in texts if getattr(t, "text", None))
                line = str(line or "").strip()
                if line:
                    lines.append(line)
            if lines:
                blocks.append(lines)
        return blocks

    para_map = {id(p._p): p for p in document.paragraphs}
    table_map = {id(t._tbl): t for t in document.tables}

    total_paragraphs = 0
    heading_paragraphs_count = 0
    bullet_paragraphs_count = 0
    table_count = 0
    body_lines: list[str] = []

    for child in document.element.body.iterchildren():
        tag = getattr(child, "tag", "") or ""
        if tag.endswith("}p"):
            paragraph = para_map.get(id(child))
            if paragraph is None:
                continue
            total_paragraphs += 1
            if _is_heading_paragraph(paragraph):
                heading_paragraphs_count += 1
            if _is_list_paragraph(paragraph) and not _is_heading_paragraph(paragraph):
                bullet_paragraphs_count += 1
            body_lines.extend(_emit_paragraph_lines(paragraph))
        elif tag.endswith("}tbl"):
            table = table_map.get(id(child))
            if table is None:
                continue
            table_count += 1

            cell_paragraphs = 0
            for row in getattr(table, "rows", []) or []:
                for cell in getattr(row, "cells", []) or []:
                    cell_paragraphs += len(getattr(cell, "paragraphs", []) or [])
            total_paragraphs += cell_paragraphs

            body_lines.append("")
            body_lines.extend(_table_to_lines(table))
            body_lines.append("")

    textboxes = _extract_textboxes()
    textbox_count = len(textboxes)

    if textboxes:
        body_lines.append("")
        for tb in textboxes:
            body_lines.append("# [TEXTBOX]")
            body_lines.extend(tb)
            body_lines.append("")

    text = "\n".join(body_lines).strip()

    header_text, footer_text = _extract_headers_footers()
    had_header_footer = bool(header_text or footer_text)

    debug: dict[str, object] = {
        "docx_header": header_text,
        "docx_footer": footer_text,
        "total_paragraphs": int(total_paragraphs),
        "heading_paragraphs_count": int(heading_paragraphs_count),
        "bullet_paragraphs_count": int(bullet_paragraphs_count),
        "table_count": int(table_count),
        "textbox_count": int(textbox_count),
        "had_header_footer": bool(had_header_footer),
    }

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
# HEADER / FOOTER STRIPPER (single definition; see above)
# ============================================================
