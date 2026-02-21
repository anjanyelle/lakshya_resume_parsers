from __future__ import annotations

from collections import Counter
import logging
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from statistics import median

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


def reconstruct_two_column_layout(blocks: list[LayoutBlock]) -> str:
    if not blocks:
        return ""

    min_x0 = min(b.x0 for b in blocks)
    max_x1 = max(b.x1 for b in blocks)
    page_width = max(1.0, max_x1 - min_x0)
    midpoint = min_x0 + (page_width * 0.5)

    heights = [b.height for b in blocks if b.height > 0]
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

    def _is_full_width(b: LayoutBlock) -> bool:
        return b.width >= (page_width * 0.85)

    def _token_stats(lines: list[str]) -> tuple[float, float]:
        tokens: list[str] = []
        for ln in lines:
            tokens.extend([t for t in ln.split() if t])
        if not tokens:
            return 0.0, 0.0
        digitish = 0
        longish = 0
        for t in tokens:
            if any(ch.isdigit() for ch in t) or _MONTH_HINT_RE.search(t):
                digitish += 1
            if len(t) >= 8:
                longish += 1
        denom = max(1, len(tokens))
        return digitish / denom, longish / denom

    full_width = [b for b in blocks if _is_full_width(b)]
    non_full = [b for b in blocks if not _is_full_width(b)]

    left = [b for b in non_full if b.x_center < midpoint]
    right = [b for b in non_full if b.x_center >= midpoint]

    full_width_sorted = sorted(full_width, key=lambda b: (b.y0, b.x0))
    left_sorted = sorted(left, key=lambda b: (b.y0, b.x0))
    right_sorted = sorted(right, key=lambda b: (b.y0, b.x0))

    two_column = bool(left_sorted) and bool(right_sorted)
    if two_column:
        right_lines = [b.text.strip() for b in right_sorted if b.text.strip()]
        digitish_ratio, longish_ratio = _token_stats(right_lines)
        right_x0 = min((b.x0 for b in right_sorted), default=min_x0)
        right_x1 = max((b.x1 for b in right_sorted), default=max_x1)
        right_width_ratio = max(0.0, (right_x1 - right_x0) / page_width)

        row_merge_mode = (
            digitish_ratio >= 0.45
            and longish_ratio <= 0.45
            and right_width_ratio >= 0.25
        )
        if not row_merge_mode:
            main_blocks = sorted(full_width_sorted + left_sorted, key=lambda b: (b.y0, b.x0))
            side_blocks = right_sorted

            def _emit_blocks(col: list[LayoutBlock]) -> list[str]:
                out_lines: list[str] = []
                heights2 = [b.height for b in col if b.height > 0]
                avg_h2 = (sum(heights2) / len(heights2)) if heights2 else typical_h
                gap_threshold2 = max(10.0, avg_h2 * 1.5)
                for i, b in enumerate(col):
                    ln = b.text.strip()
                    if ln:
                        out_lines.append(ln)
                    if i < (len(col) - 1):
                        next_b = col[i + 1]
                        gap = next_b.y0 - b.y1
                        next_preview = next_b.text.strip()
                        break_by_gap = gap > gap_threshold2
                        break_by_punct = (
                            ln.rstrip().endswith((".", "!", "?", ":", ";"))
                            and _starts_upper(next_preview)
                        )
                        if _is_bullet_line(ln) or _is_bullet_line(next_preview):
                            break_by_punct = False
                        if break_by_gap or break_by_punct:
                            out_lines.append("")
                return out_lines

            out = _emit_blocks(main_blocks)
            if out and side_blocks:
                out.append("")
            out.extend(_emit_blocks(side_blocks))
            return "\n".join(out).strip()

    fw_i = 0
    l_i = 0
    r_i = 0

    rows: list[tuple[float, float, list[LayoutBlock]]] = []

    def _consume_row(col: list[LayoutBlock], start_idx: int, row_y0: float, row_y1: float) -> tuple[list[LayoutBlock], int, float, float]:
        out: list[LayoutBlock] = []
        idx = start_idx
        while idx < len(col):
            b = col[idx]
            overlap = min(b.y1, row_y1) - max(b.y0, row_y0)
            if overlap >= 0.0 or abs(b.y0 - row_y0) <= y_tol:
                out.append(b)
                row_y0 = min(row_y0, b.y0)
                row_y1 = max(row_y1, b.y1)
                idx += 1
                continue
            break
        return out, idx, row_y0, row_y1

    while fw_i < len(full_width_sorted) or l_i < len(left_sorted) or r_i < len(right_sorted):
        next_fw = full_width_sorted[fw_i] if fw_i < len(full_width_sorted) else None
        next_l = left_sorted[l_i] if l_i < len(left_sorted) else None
        next_r = right_sorted[r_i] if r_i < len(right_sorted) else None

        candidates: list[LayoutBlock] = [b for b in [next_fw, next_l, next_r] if b is not None]
        if not candidates:
            break
        next_block = min(candidates, key=lambda b: (b.y0, b.x0))

        if next_fw is not None and next_block is next_fw:
            rows.append((next_fw.y0, next_fw.y1, [next_fw]))
            fw_i += 1
            continue

        row_y0 = next_block.y0
        row_y1 = next_block.y1

        row_blocks: list[LayoutBlock] = []
        left_row, l_i, row_y0, row_y1 = _consume_row(left_sorted, l_i, row_y0, row_y1)
        right_row, r_i, row_y0, row_y1 = _consume_row(right_sorted, r_i, row_y0, row_y1)

        row_blocks.extend(left_row)
        row_blocks.extend(right_row)
        row_blocks = sorted(row_blocks, key=lambda b: b.x0)
        if row_blocks:
            rows.append((row_y0, row_y1, row_blocks))

    out_lines: list[str] = []
    row_heights = [(y1 - y0) for (y0, y1, _) in rows if (y1 - y0) > 0]
    avg_row_h = (sum(row_heights) / len(row_heights)) if row_heights else typical_h
    gap_threshold = max(10.0, avg_row_h * 1.5)
    for i, (y0, y1, row_blocks) in enumerate(rows):
        line = " | ".join(b.text.strip() for b in row_blocks if b.text.strip()).strip()
        if line:
            out_lines.append(line)
        if i < (len(rows) - 1):
            next_y0 = rows[i + 1][0]
            gap = next_y0 - y1
            next_line_preview = " | ".join(
                b.text.strip() for b in rows[i + 1][2] if b.text.strip()
            ).strip()
            break_by_gap = gap > gap_threshold
            break_by_punct = (
                line.rstrip().endswith((".", "!", "?", ":", ";"))
                and _starts_upper(next_line_preview)
            )
            if _is_bullet_line(line) or _is_bullet_line(next_line_preview):
                break_by_punct = False
            if break_by_gap or break_by_punct:
                out_lines.append("")

    return "\n".join(out_lines).strip()


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
            text=normalize_resume_text(ocr_text),
            ocr_confidence=ocr_conf,
            used_ocr=True,
            method="ocr",
        )

    return ExtractedText(text=normalize_resume_text(text), method=method)


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

    gap_threshold = 120.0
    if page_width and page_width > 0:
        gap_threshold = max(60.0, float(page_width) * 0.12)
    two_column = False
    if split_x is not None and page_width > 0:
        left = sum(1 for w in cleaned_words if float(w["x0"]) < page_width * 0.4)
        right = sum(1 for w in cleaned_words if float(w["x0"]) > page_width * 0.6)
        total = len(cleaned_words)
        two_column = total > 0 and (left / total) > 0.15 and (right / total) > 0.15

    if two_column and split_x is not None:
        left_words = [w for w in cleaned_words if float(w["x0"]) < split_x]
        right_words = [w for w in cleaned_words if float(w["x0"]) >= split_x]

        # Heuristic: if the "right column" is mostly dates/short tokens, it's likely just
        # right-aligned metadata (e.g., job dates), not a true second column.
        if right_words:
            digitish = 0
            longish = 0
            for w in right_words:
                token = str(w.get("text") or "")
                if not token:
                    continue
                if any(ch.isdigit() for ch in token) or _MONTH_HINT_RE.search(token):
                    digitish += 1
                if len(token) >= 8:
                    longish += 1
            denom = max(1, len(right_words))
            digitish_ratio = digitish / denom
            longish_ratio = longish / denom
            if digitish_ratio >= 0.55 and longish_ratio <= 0.35:
                two_column = False

    if two_column and split_x is not None:
        left_words = [w for w in cleaned_words if float(w["x0"]) < split_x]
        right_words = [w for w in cleaned_words if float(w["x0"]) >= split_x]
        left_lines = _group_words_into_lines(left_words, gap_threshold=gap_threshold)
        right_lines = _group_words_into_lines(right_words, gap_threshold=gap_threshold)
        return left_lines + ([""] if left_lines and right_lines else []) + right_lines

    return _group_words_into_lines(cleaned_words, gap_threshold=gap_threshold)


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
