from __future__ import annotations

import re
import unicodedata


_MULTISPACE_RE = re.compile(r"[ \t]+")
_MULTILINE_RE = re.compile(r"\n{3,}")
_ZERO_WIDTH_RE = re.compile(r"[\u200b\u200c\u200d\u2060\ufeff]")
_RTL_MARKS_RE = re.compile(r"[\u200e\u200f\u202a-\u202e]")
_MULTISPACE_RUN_RE = re.compile(r"[ \t]{2,}")
_BULLET_RE = re.compile(r"[\u2022\u2023\u25E6\u2043\u2219\uf0b7\uf0a7\uf0d8\uf0fc▪]")

# Split CamelCase like:
# AWSCertifiedSolutionsArchitect -> AWS Certified Solutions Architect
_CAMEL_CASE_SPLIT_RE = re.compile(
    r"""
    (?<=[a-z])(?=[A-Z])|
    (?<=[A-Z])(?=[A-Z][a-z])|
    (?<=[A-Za-z])(?=\d)|
    (?<=\d)(?=[A-Za-z])
    """,
    re.VERBOSE,
)

def split_camel_case(text: str) -> str:
    if not text:
        return text
    return _CAMEL_CASE_SPLIT_RE.sub(" ", text)

def _repair_common_urls(text: str) -> str:
    cleaned = text
    cleaned = re.sub(r"\b(https?)\s*:\s*/\s*/\s*", r"\1://", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bwww\s*\.\s*", "www.", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(
        r"\blinkedin\s*\.\s*com\s*/\s*(in|pub)\s*/\s*",
        r"linkedin.com/\1/",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"\bgithub\s*\.\s*com\s*/\s*",
        "github.com/",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\b(linkedin\.com|github\.com)\s*/\s*", r"\1/", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(https?://|www\.)\s+", r"\1", cleaned, flags=re.IGNORECASE)
    return cleaned


def normalize_text(text: str) -> str:
    cleaned = unicodedata.normalize("NFKC", text)
    cleaned = split_camel_case(cleaned)
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = _ZERO_WIDTH_RE.sub("", cleaned)
    cleaned = _RTL_MARKS_RE.sub("", cleaned)
    cleaned = _BULLET_RE.sub("- ", cleaned)
    cleaned = cleaned.replace("•", "- ").replace("–", "-").replace("—", "-")
    cleaned = _repair_common_urls(cleaned)
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
    cleaned = _BULLET_RE.sub("- ", cleaned)
    cleaned = cleaned.replace("•", "- ").replace("–", "-").replace("—", "-")
    cleaned = _repair_common_urls(cleaned)
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
    #Enterprise Upgrade: Split CamelCase Certifications
    cleaned = split_camel_case(cleaned)
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