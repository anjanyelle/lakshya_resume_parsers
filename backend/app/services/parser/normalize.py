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
    # Split CamelCase
    s = _CAMEL_CASE_SPLIT_RE.sub(" ", text)
    # Enterprise Fix: Repair incorrect "Aust In" / "Berl In" / "Dubl In" splitting caused by OCR normalization
    if " In" in s or " At" in s:
        s = re.sub(r"\b(Aust|Berl|Dubl|Lubl|Pek|Tall|Turk|Indi|Chatt|Urb|Beng|Kal)\s+In\b", r"\1in", s, flags=re.IGNORECASE)
        s = re.sub(r"\b(At)\s+(lanta)\b", r"\1\2", s, flags=re.IGNORECASE)
    return s


def normalize_table_lines(text: str) -> str:
    """Normalize DOCX table-style text: treat tab/multi-space separators as line breaks so each cell is on its own line."""
    if not text or not text.strip():
        return text
    lines = text.splitlines()
    out_lines: list[str] = []
    for line in lines:
        parts = re.split(r"[\t ]{2,}", line)
        parts = [p.strip() for p in parts if p.strip()]
        if parts:
            out_lines.extend(parts)
        else:
            out_lines.append(line.strip())
    return "\n".join(out_lines)


def _normalize_table_lines_with_stats(text: str) -> tuple[str, bool, int]:
    """Run normalize_table_lines on text; return (cleaned_text, applied, approximate rows normalized)."""
    if not text or not text.strip():
        return text, False, 0
    cleaned = normalize_table_lines(text)
    applied = cleaned != text
    count = max(0, cleaned.count("\n") - text.count("\n")) if applied else 0
    return cleaned, applied, count


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
    # Enterprise: repair city names wrongly split by ([a-z])in([A-Z]) (e.g. "Aust in Austin" / "Aust in  Austin" -> "Austin Austin")
    s = re.sub(r"\b(Aust|Berl|Dubl|Lubl|Pek|Tall|Turk|Indi|Chatt|Urb|Beng|Kal)\s+in\s+", r"\1in ", s, flags=re.IGNORECASE)
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


def clean_summary_and_skills_sections(payload: dict) -> tuple[dict, dict]:
    """Normalize summary/skills sections: dedupe lines, move skill-like content from summary to skills, sentence-like from skills to summary.
    Treats 'technical_skills' section as 'skills' so both headings render skills correctly."""
    if not isinstance(payload, dict):
        return payload, {"moved_summary_to_skills": 0, "moved_skills_to_summary": 0}

    out = {k: dict(v) if isinstance(v, dict) else v for k, v in payload.items()}
    counts = {"moved_summary_to_skills": 0, "moved_skills_to_summary": 0}

    summary_block = out.get("summary")
    skills_block = out.get("skills")
    tech_skills_block = out.get("technical_skills")
    if isinstance(tech_skills_block, dict) and isinstance(skills_block, dict):
        sc = str(skills_block.get("content") or "").strip()
        tc = str(tech_skills_block.get("content") or "").strip()
        if tc and (not sc or tc != sc):
            skills_block = {**skills_block, "content": "\n".join(filter(None, [sc, tc]))}
    elif isinstance(tech_skills_block, dict) and not isinstance(skills_block, dict):
        skills_block = dict(tech_skills_block)
        out["skills"] = skills_block
    if not isinstance(summary_block, dict):
        summary_block = {}
    if not isinstance(skills_block, dict):
        skills_block = {}

    summary_content = str(summary_block.get("content") or "").strip()
    skills_content = str(skills_block.get("content") or "").strip()

    summary_lines = [ln.strip() for ln in summary_content.splitlines() if ln.strip()]
    skills_lines = [ln.strip() for ln in skills_content.splitlines() if ln.strip()]

    out_lines: list[str] = []
    applied = False
    normalized_rows = 0

    for raw_line in text.splitlines():
        line = raw_line.rstrip("\r")
        stripped = line.strip()
        if not stripped or "|" not in stripped or not _TABLE_PIPE_ROW_RE.match(stripped):
            out_lines.append(line)
            continue

        cells = [c.strip() for c in stripped.split("|")]
        cells = [c for c in cells if c]
        if len(cells) < 2:
            out_lines.append(line)
            continue

        date_cells = [c for c in cells if _looks_date_like(c)]
        company_title_like = sum(1 for c in cells[:3] if _looks_company_or_title_like(c))

        is_headerish = bool(date_cells) and company_title_like >= 2
        if is_headerish:
            company = cells[0] if len(cells) >= 1 else ""
            title = cells[1] if len(cells) >= 2 else ""
            date_range = ""
            for c in reversed(cells):
                if _looks_date_like(c):
                    date_range = c
                    break
            if not date_range and len(cells) >= 3:
                date_range = cells[2]

            rendered = " | ".join([p for p in [company, title, date_range] if p]).strip()
            out_lines.append(rendered if rendered else line)
            continue

        longish = any(len(c) >= 45 or c.count(" ") >= 7 for c in cells)
        if longish:
            applied = True
            normalized_rows += 1
            for c in cells:
                cleaned = c.strip()
                if not cleaned:
                    continue
                if cleaned.startswith("-"):
                    out_lines.append(cleaned)
                else:
                    out_lines.append(f"- {cleaned}")
            continue

        out_lines.append(line)

    return "\n".join(out_lines), applied, normalized_rows





# Headings that indicate skills content — summary must stop before these
_SUMMARY_STOP_AT_SKILLS_RE = re.compile(
    r"^(?:technical\s+skills?\s*[:\-–—]?|skills?\s*[:\-–—]?|core\s+competencies\s*[:\-–—]?|"
    r"databases?\s*&\s*data\s+stores?\s*[:\-–—]?|programming\s+languages?\s*[:\-–—]?|"
    r"exhaustive\s+technical\s+skill\s+matrix|technologies?\s*[:\-–—]|"
    r"tech\s+stack\s*[:\-–—]|tools?\s*[:\-–—]|frameworks?\s*[:\-–—]).*$",
    re.IGNORECASE,
)


def clean_summary_and_skills_sections(
    sections: dict,
) -> tuple[dict, dict[str, int]]:
    if not isinstance(sections, dict) or not sections:
        return sections, {"moved_summary_to_skills": 0, "moved_skills_to_summary": 0}

    summary_block = sections.get("summary") if isinstance(sections.get("summary"), dict) else None
    skills_block = sections.get("skills") if isinstance(sections.get("skills"), dict) else None
    if not isinstance(summary_block, dict) or not isinstance(skills_block, dict):
        return sections, {"moved_summary_to_skills": 0, "moved_skills_to_summary": 0}

    summary_text = str(summary_block.get("content") or "")
    # Truncate summary at skills headers — prevents skills bleeding into summary
    summary_lines_raw = summary_text.splitlines()
    truncated: list[str] = []
    for ln in summary_lines_raw:
        stripped = ln.strip()
        if _SUMMARY_STOP_AT_SKILLS_RE.match(stripped):
            break
        truncated.append(ln)
    summary_text = "\n".join(truncated).strip()
    skills_text = str(skills_block.get("content") or "")

    def is_skill_like(line: str) -> bool:
        parts = [p.strip() for p in line.split(",") if p.strip()]
        return len(parts) >= 3

    def is_sentence_like(line: str) -> bool:
        line_lower = line.lower()
        if len(line.split()) < 4:
            return False
        if line_lower.startswith(("i ", "we ", "my ", "i'm ", "i've ")):
            return True
        if any(w in line_lower for w in (" led ", " lead ", " managed ", " built ", " developed ")):
            return True
        return False

    to_skills: list[str] = []
    to_summary: list[str] = []
    new_summary: list[str] = []
    new_skills: list[str] = []

    for ln in deduped_summary:
        if is_skill_like(ln):
            to_skills.append(ln)
            counts["moved_summary_to_skills"] += 1
        else:
            new_summary.append(ln)

    for ln in skills_lines:
        if is_sentence_like(ln):
            to_summary.append(ln)
            counts["moved_skills_to_summary"] += 1
        else:
            new_skills.append(ln)

    out["summary"] = {**summary_block, "content": "\n".join(new_summary + to_summary)}
    out["skills"] = {**skills_block, "content": "\n".join(new_skills + to_skills)}

    return out, counts
