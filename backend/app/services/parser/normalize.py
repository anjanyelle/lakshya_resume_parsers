from __future__ import annotations

import re
import unicodedata


_MULTISPACE_RE = re.compile(r"[ \t]+")
_MULTILINE_RE = re.compile(r"\n{3,}")
_ZERO_WIDTH_RE = re.compile(r"[\u200b\u200c\u200d\u2060\ufeff]")
_RTL_MARKS_RE = re.compile(r"[\u200e\u200f\u202a-\u202e]")


def normalize_text(text: str) -> str:
    cleaned = unicodedata.normalize("NFKC", text)
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = _ZERO_WIDTH_RE.sub("", cleaned)
    cleaned = _RTL_MARKS_RE.sub("", cleaned)
    cleaned = cleaned.replace("•", "- ").replace("–", "-").replace("—", "-")
    cleaned = _MULTISPACE_RE.sub(" ", cleaned)
    cleaned = _MULTILINE_RE.sub("\n\n", cleaned)
    cleaned = cleaned.strip()
    cleaned = fix_ocr_errors(cleaned)
    return cleaned


def fix_ocr_errors(text: str) -> str:
    # Replace 0 with O when surrounded by letters
    text = re.sub(r"(?<=[A-Za-z])0(?=[A-Za-z])", "O", text)
    # Replace O with 0 when surrounded by digits
    text = re.sub(r"(?<=\d)O(?=\d)", "0", text)
    # Replace l with 1 when surrounded by digits
    text = re.sub(r"(?<=\d)l(?=\d)", "1", text)
    # Replace I with 1 when surrounded by digits
    text = re.sub(r"(?<=\d)I(?=\d)", "1", text)
    return text
