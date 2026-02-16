from __future__ import annotations

import re
import unicodedata


_MULTISPACE_RE = re.compile(r"[ \t]+")
_MULTILINE_RE = re.compile(r"\n{3,}")
_ZERO_WIDTH_RE = re.compile(r"[\u200b\u200c\u200d\u2060\ufeff]")
_RTL_MARKS_RE = re.compile(r"[\u200e\u200f\u202a-\u202e]")
_MULTISPACE_RUN_RE = re.compile(r"[ \t]{2,}")


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


def normalize_resume_text(text: str) -> str:
    cleaned = unicodedata.normalize("NFKC", text)
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = _ZERO_WIDTH_RE.sub("", cleaned)
    cleaned = _RTL_MARKS_RE.sub("", cleaned)
    cleaned = cleaned.replace("•", "- ").replace("–", "-").replace("—", "-")
    cleaned = cleaned.replace("\t", "    ")

    def _preserve_columns(match: re.Match[str]) -> str:
        run = match.group(0)
        if not run:
            return " "
        if "\t" in run:
            run = run.replace("\t", "    ")
        return "  "

    cleaned = _MULTISPACE_RUN_RE.sub(_preserve_columns, cleaned)
    cleaned = _MULTILINE_RE.sub("\n\n", cleaned)
    cleaned = "\n".join(line.rstrip() for line in cleaned.split("\n"))
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

    def _fix_token(match: re.Match[str]) -> str:
        token = match.group(0)
        if not token:
            return token
        letters = sum(1 for c in token if c.isalpha())
        digits = sum(1 for c in token if c.isdigit())
        if digits >= 2 and letters <= 2:
            token = re.sub(r"^[lI](?=\d)", "1", token)
            token = re.sub(r"(?<=\d)[lI](?=\d)", "1", token)
            token = re.sub(r"(?<=\d)O(?=\d)", "0", token)
            return token
        return token

    text = re.sub(r"\b[A-Za-z0-9]{2,}\b", _fix_token, text)
    return text
