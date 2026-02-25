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


def _apply_ocr_fixes(text: str, fixes: dict[str, str]) -> str:
    """Apply character substitutions only in word context (not in numbers or dates)."""
    for bad, good in fixes.items():
        text = re.sub(
            rf"(?<=[A-Za-z]){re.escape(bad)}(?=[A-Za-z])",
            good,
            text,
        )
    return text


def normalize_resume_text(
    text: str,
    *,
    source_format: str | None = None,
) -> str:
    cleaned = unicodedata.normalize("NFKC", text)
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = _ZERO_WIDTH_RE.sub("", cleaned)
    cleaned = _RTL_MARKS_RE.sub("", cleaned)
    cleaned = _BULLET_RE.sub("- ", cleaned)
    cleaned = cleaned.replace("•", "- ").replace("–", "-").replace("—", "-")
    cleaned = _repair_common_urls(cleaned)
    cleaned = cleaned.replace("\t", "    ")

    if source_format == "pdf":
        cleaned = re.sub(r"(\w+)-\n(\w+)", r"\1\2", cleaned)
        cleaned = cleaned.replace("\ufb01", "fi").replace("\ufb02", "fl").replace("\ufb00", "ff")
    elif source_format in ("docx", "doc"):
        cleaned = normalize_table_lines(cleaned)
        cleaned = re.sub(r"\f", "\n\n", cleaned)
    elif source_format == "ocr":
        ocr_fixes = {"0": "O", "1": "I", "|": "I", "5": "S"}
        cleaned = _apply_ocr_fixes(cleaned, ocr_fixes)

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


def fix_concatenated_words(s: str) -> str:
    """Insert spaces in concatenated words (e.g. IndianInstituteofTechnology -> Indian Institute of Technology).
    Handles PDF/OCR output or pipeline text that lost spaces between words."""
    if not s or len(s) < 3:
        return s
    # "of" or "at" followed by uppercase -> insert space (e.g. "InstituteofTechnology" -> "Institute of Technology")
    s = re.sub(r"\b(of|at)([A-Z])", r"\1 \2", s, flags=re.IGNORECASE)
    # lowercase letter + "of" + uppercase (e.g. "InstituteofTechnology", "CollegeofBusiness")
    s = re.sub(r"([a-z])of([A-Z])", r"\1 of \2", s)
    # lowercase letter + "in" + uppercase (e.g. "Sciencein", "Excellencein", "Allocationin")
    s = re.sub(r"([a-z])in([A-Z])", r"\1 in \2", s)
    # lowercase letter + "in" + space + uppercase (e.g. "Sciencein Computer" -> "Science in Computer")
    s = re.sub(r"([a-z])in(\s+)([A-Z])", r"\1 in \2\3", s)
    # lowercase letter + "at" + uppercase (e.g. "Texasat" -> "Texas at")
    s = re.sub(r"([a-z])at([A-Z])", r"\1 at \2", s)
    # lowercase letter + "at" + space + uppercase (e.g. "Texasat Austin" -> "Texas at Austin")
    s = re.sub(r"([a-z])at(\s+)([A-Z])", r"\1 at \2\3", s)
    # lowercase letter + "of" + space + uppercase (e.g. "Instituteof Technology", "Collegeof Business")
    s = re.sub(r"([a-z])of(\s+)([A-Z])", r"\1 of \3", s)
    # "of" + "the" with no space (e.g. "Recipientofthe", "Presidentofthe")
    s = re.sub(r"of(the)\b", r" of \1", s, flags=re.IGNORECASE)
    # lowercase letter + "for" + uppercase (e.g. "Fellowshipfor" -> "Fellowship for")
    s = re.sub(r"([a-z])for([A-Z])", r"\1 for \2", s)
    s = re.sub(r"([a-z])for(\s+)([A-Z])", r"\1 for \2\3", s)
    # semicolon without space before capital (e.g. "Summa Cum Laude;President" -> "; President")
    s = re.sub(r";([A-Z])", r"; \1", s)
    # comma without space before capital (e.g. "Cambridge,MA", "Washington,Seattle,WA"); avoid double space
    s = re.sub(r",(?=[A-Z])(?!\s)", r", ", s)
    # short abbreviation (2–4 caps) + word (e.g. "UWComputer", "UTComputer", "CMUExcellence", "MITPresidential"); avoid breaking "University"
    s = re.sub(r"\b(UW|UT|CMU|MIT|USC|NYU|UCLA|UNC)([A-Z][a-z])", r"\1 \2", s)
    # period + caps + word (e.g. ".NETMicroservices" -> ".NET Microservices")
    s = re.sub(r"(\.)([A-Z]{2,})([A-Z][a-z]+)", r"\1\2 \3", s)
    # letter + "&" + letter (e.g. "Management&Operations" -> "Management & Operations")
    s = re.sub(r"([A-Za-z])(&)([A-Za-z])", r"\1 \2 \3", s)
    # ")%" or ")letter" without space after comma (e.g. "Business),At" -> "Business), At")
    s = re.sub(r"(\))\s*,([A-Za-z])", r"\1, \2", s)
    # All-caps compound institution names (e.g. "MYUNIVERSITY" -> "MY UNIVERSITY")
    s = re.sub(r"\bMYUNIVERSITY\b", "MY UNIVERSITY", s, flags=re.IGNORECASE)
    # "Top5%" / "Top10%" etc.
    s = re.sub(r"([A-Za-z])(\d%?)", r"\1 \2", s)
    # lowercase followed by uppercase -> insert space (e.g. "IndianInstitute" -> "Indian Institute")
    s = re.sub(r"([a-z])([A-Z])", r"\1 \2", s)
    # letter followed by ( -> insert space (e.g. "Technology(IIT)" -> "Technology (IIT)")
    s = re.sub(r"([a-zA-Z])(\()", r"\1 \2", s)
    # ) followed by letter -> insert space (e.g. "IIT),Bombay" -> "IIT) , Bombay")
    s = re.sub(r"(\))([A-Za-z])", r"\1 \2", s)
    # digit followed by uppercase word (e.g. "2015TestCase" -> "2015 TestCase") so noise can be stripped
    s = re.sub(r"(\d)([A-Z][a-z])", r"\1 \2", s)
    return s


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
