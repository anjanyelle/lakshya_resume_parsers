from __future__ import annotations

import re
import unicodedata


_MULTISPACE_RE = re.compile(r"[ \t]+")
_MULTILINE_RE = re.compile(r"\n{3,}")
_ZERO_WIDTH_RE = re.compile(r"[\u200b\u200c\u200d\u2060\ufeff]")
_RTL_MARKS_RE = re.compile(r"[\u200e\u200f\u202a-\u202e]")
_MULTISPACE_RUN_RE = re.compile(r"[ \t]{2,}")
_BULLET_RE = re.compile(r"[\u2022\u2023\u25E6\u2043\u2219\uf0b7\uf0a7\uf0d8\uf0fc▪]")

_TABLE_PIPE_ROW_RE = re.compile(r"^[^\|]+\|[^\|]+(\|[^\|]+)*$")
_MONTH_RE = re.compile(
    r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)\b",
    re.IGNORECASE,
)
_YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")
_DATE_SEP_RE = re.compile(r"\b\d{1,2}[\-/]\d{2,4}\b")

_TECH_KEYWORD_RE = re.compile(
    r"\b(python|java|javascript|typescript|react|node(?:\.js)?|docker|kubernetes|aws|azure|gcp|sql|postgres(?:ql)?|mysql|redis|kafka|spark|terraform|jenkins|git|linux|fastapi|django|flask)\b",
    re.IGNORECASE,
)
_VERB_HINT_RE = re.compile(
    r"\b(develop(?:ed|ing)?|build(?:s|ing|t)?|implement(?:ed|ing)?|manage(?:d|ment|s)?|lead(?:s|ing)?|led|design(?:ed|ing)?|create(?:d|ing)?|optimi[sz](?:ed|ing)?|deliver(?:ed|ing)?|responsible\s+for|collaborat(?:ed|ing)|improv(?:ed|ing))\b",
    re.IGNORECASE,
)
_PRONOUN_HINT_RE = re.compile(r"\b(i|my|me|we|our)\b|\bresponsible\s+for\b", re.IGNORECASE)


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


def _looks_date_like(value: str) -> bool:
    cleaned = (value or "").strip()
    if not cleaned:
        return False
    lowered = cleaned.lower()
    if "present" in lowered or "current" in lowered:
        return True
    if _MONTH_RE.search(cleaned):
        return True
    if _YEAR_RE.search(cleaned):
        return True
    if _DATE_SEP_RE.search(cleaned):
        return True
    return False


def _looks_company_or_title_like(value: str) -> bool:
    cleaned = re.sub(r"\s+", " ", (value or "")).strip()
    if not cleaned:
        return False
    if len(cleaned) > 90:
        return False
    letters = sum(1 for ch in cleaned if ch.isalpha())
    if letters < 2:
        return False
    return True


def _normalize_table_lines_with_stats(text: str) -> tuple[str, bool, int]:
    if not text:
        return text, False, 0

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


def normalize_table_lines(text: str) -> str:
    normalized, _, _ = _normalize_table_lines_with_stats(text)
    return normalized


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
    skills_text = str(skills_block.get("content") or "")

    summary_lines = [ln.strip() for ln in summary_text.splitlines() if ln.strip()]
    skills_lines = [ln.strip() for ln in skills_text.splitlines() if ln.strip()]

    def _is_skill_like(line: str) -> bool:
        cleaned = (line or "").strip("-•* \t").strip()
        if not cleaned:
            return False
        if _TECH_KEYWORD_RE.search(cleaned):
            return True
        tokens = [t.strip() for t in re.split(r"[,/|·]", cleaned) if t.strip()]
        if len(tokens) >= 3 and all(1 <= len(t) <= 25 for t in tokens) and len(cleaned) <= 120:
            return True
        if cleaned.count(",") >= 2 and len(cleaned) <= 120:
            return True
        if re.fullmatch(r"[A-Za-z0-9 +#./-]{2,35}", cleaned) and len(cleaned.split()) <= 4:
            return True
        return False

    def _is_sentence_like(line: str, *, min_len: int) -> bool:
        cleaned = (line or "").strip()
        if len(cleaned) < min_len:
            return False
        if cleaned.count(" ") < 6:
            return False
        if _VERB_HINT_RE.search(cleaned) or _PRONOUN_HINT_RE.search(cleaned):
            return True
        if cleaned.endswith(".") and len(cleaned) >= min_len:
            return True
        return False

    moved_to_skills: list[str] = []
    kept_summary: list[str] = []
    for ln in summary_lines:
        if _is_skill_like(ln) and not _is_sentence_like(ln, min_len=40):
            moved_to_skills.append(ln)
        else:
            kept_summary.append(ln)

    moved_to_summary: list[str] = []
    kept_skills: list[str] = []
    for ln in skills_lines:
        if _is_sentence_like(ln, min_len=60):
            moved_to_summary.append(ln)
        else:
            kept_skills.append(ln)

    moved_summary_to_skills = len(moved_to_skills)
    moved_skills_to_summary = len(moved_to_summary)

    out_sections = dict(sections)
    out_summary = dict(summary_block)
    out_skills = dict(skills_block)

    if moved_skills_to_summary:
        out_summary["content"] = "\n".join([*kept_summary, *moved_to_summary]).strip()
        out_summary["content_corrected"] = True
    if moved_summary_to_skills:
        out_skills["content"] = "\n".join([*kept_skills, *moved_to_skills]).strip()
        out_skills["content_corrected"] = True

    out_sections["summary"] = out_summary
    out_sections["skills"] = out_skills

    return out_sections, {
        "moved_summary_to_skills": int(moved_summary_to_skills),
        "moved_skills_to_summary": int(moved_skills_to_summary),
    }
