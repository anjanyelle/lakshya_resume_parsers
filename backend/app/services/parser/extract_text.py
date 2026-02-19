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
    debug: dict[str, object] = {}

    try:
        pymupdf_text = extract_text_from_pdf_pymupdf_layout(file_path)
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
            debug=debug or None,
        )

    return ExtractedText(text=normalize_resume_text(text), method=method, debug=debug or None)


def _extract_pdf_pymupdf_blocks(file_path: Path) -> str:
    try:
        import fitz  # type: ignore
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError("PyMuPDF not installed") from exc

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


def extract_text_from_pdf_pymupdf_layout(file_path: Path) -> str:
    try:
        import fitz  # type: ignore
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError("PyMuPDF not installed") from exc

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
                    cleaned = _clean_fragment(raw)
                    if not cleaned:
                        continue
                    items.append(LayoutBlock(x0=x0, y0=y0, x1=x1, y1=y1, text=cleaned))

            if not items:
                page_text = _clean_fragment(page.get_text("text") or "")
                if page_text:
                    pages_out.append(page_text)
                continue

            page_out = reconstruct_two_column_layout(items).strip()
            if page_out:
                pages_out.append(page_out)
    finally:
        doc.close()

    pages_lines: list[list[str]] = []
    for p in pages_out:
        pages_lines.append(p.split("\n"))
    pages_lines = _strip_repeated_headers_footers(pages_lines)
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


def _extract_pdf_page_lines_pdfplumber(page: object) -> tuple[list[str], dict[str, object]]:
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
        right_words = [w for w in cleaned_words if float(w["x0"]) >= split_x]
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

    def _words_to_lines(ws: list[dict[str, object]]) -> list[tuple[float, float, str]]:
        if not ws:
            return []
        ws_sorted = sorted(ws, key=lambda w: (float(w["top"]), float(w["x0"])))
        bins: list[dict[str, object]] = []
        for w in ws_sorted:
            y0 = float(w["top"])
            y1 = float(w["bottom"])
            if not bins:
                bins.append({"y0": y0, "y1": y1, "words": [w]})
                continue
            last = bins[-1]
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
                bins.append({"y0": y0, "y1": y1, "words": [w]})

        out: list[tuple[float, float, str]] = []
        for b in bins:
            b_words = b.get("words", [])
            if not isinstance(b_words, list) or not b_words:
                continue
            sorted_words = sorted(b_words, key=lambda w: float(w["x0"]))
            parts: list[str] = []
            last_x1: float | None = None
            for ww in sorted_words:
                token = str(ww.get("text") or "")
                if not token:
                    continue
                x0 = float(ww.get("x0") or 0.0)
                x1 = float(ww.get("x1") or x0)
                if last_x1 is not None and (x0 - last_x1) >= gap_threshold:
                    parts.append("|")
                parts.append(token)
                last_x1 = x1
            line = " ".join(parts).strip()
            if line:
                out.append((float(b["y0"]), float(b["y1"]), line))
        return out

    if two_column and split_x is not None:
        left_words = [w for w in cleaned_words if float(w["x0"]) < split_x]
        right_words = [w for w in cleaned_words if float(w["x0"]) >= split_x]
        left_bins = _words_to_lines(left_words)
        right_bins = _words_to_lines(right_words)

        def _with_paragraphs(bins: list[tuple[float, float, str]]) -> list[str]:
            out_lines: list[str] = []
            heights2 = [(y1 - y0) for (y0, y1, _) in bins if (y1 - y0) > 0]
            avg_h2 = (sum(heights2) / len(heights2)) if heights2 else typical_h
            gap_threshold2 = max(10.0, avg_h2 * 1.5)
            for i, (y0, y1, ln) in enumerate(bins):
                out_lines.append(ln)
                if i < (len(bins) - 1):
                    next_y0 = bins[i + 1][0]
                    gap = next_y0 - y1
                    next_ln = bins[i + 1][2]
                    break_by_gap = gap > gap_threshold2
                    break_by_punct = (
                        ln.rstrip().endswith((".", "!", "?", ":", ";"))
                        and _starts_upper(next_ln)
                    )
                    if _is_bullet_line(ln) or _is_bullet_line(next_ln):
                        break_by_punct = False
                    if break_by_gap or break_by_punct:
                        out_lines.append("")
            return out_lines

        left_lines = _with_paragraphs(left_bins)
        right_lines = _with_paragraphs(right_bins)
        lines = left_lines + ([""] if left_lines and right_lines else []) + right_lines
        nonempty = sum(1 for ln in lines if ln.strip())
        return lines, {"detected_columns": 2, "line_count": int(nonempty)}

    bins = _words_to_lines(cleaned_words)
    out_lines2: list[str] = []
    heights3 = [(y1 - y0) for (y0, y1, _) in bins if (y1 - y0) > 0]
    avg_h3 = (sum(heights3) / len(heights3)) if heights3 else typical_h
    gap_threshold3 = max(10.0, avg_h3 * 1.5)
    for i, (y0, y1, ln) in enumerate(bins):
        out_lines2.append(ln)
        if i < (len(bins) - 1):
            next_y0 = bins[i + 1][0]
            gap = next_y0 - y1
            next_ln = bins[i + 1][2]
            break_by_gap = gap > gap_threshold3
            break_by_punct = (
                ln.rstrip().endswith((".", "!", "?", ":", ";"))
                and _starts_upper(next_ln)
            )
            if _is_bullet_line(ln) or _is_bullet_line(next_ln):
                break_by_punct = False
            if break_by_gap or break_by_punct:
                out_lines2.append("")
    nonempty2 = sum(1 for ln in out_lines2 if ln.strip())
    return out_lines2, {"detected_columns": 1, "line_count": int(nonempty2)}


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
