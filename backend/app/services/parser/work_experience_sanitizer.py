from __future__ import annotations

import logging
import re
from typing import Any

from app.services.parser.work_experience_parser import ENVIRONMENT_LINE_RE, WorkExperienceParser

logger = logging.getLogger(__name__)


_PLACEHOLDER_RE = re.compile(
    r"^(?:company(?:\s*name)?|client(?:\s*name)?|organization|employer|designation|title(?:\s*role)?|role(?:\s*title)?|position|description)\b",
    re.IGNORECASE,
)

# Strip common "(Client: ...)", "(Client)", "End Client: ...", "(Client:" garbage garbage appended to company names
_COMPANY_CLIENT_SUFFIX_RE = re.compile(
    r"\s*[\(\[]\s*(?:end\s+)?client[:\s].*$|\s*[\(\[]\s*client\s*[\)\]]?.*$|\s+\(client[:\s].*$",
    re.IGNORECASE,
)

# Strip "End Client:" label prefix used when whole string is a client label
_COMPANY_CLIENT_PREFIX_RE = re.compile(
    r"^(?:end\s+)?client\s*[:\-–—]\s*",
    re.IGNORECASE,
)


def _clean_company_name(value: str) -> str:
    """Remove client-label suffixes/prefixes from a company name string."""
    if not value:
        return value
    cleaned = _COMPANY_CLIENT_SUFFIX_RE.sub("", value).strip().strip("([ ")
    cleaned = _COMPANY_CLIENT_PREFIX_RE.sub("", cleaned).strip()
    return cleaned

_LOCATION_AS_TITLE_RE = re.compile(r"^[A-Za-z ]+,\s*[A-Z][a-z]?$")


def _collapse_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        value = str(value)
    return _collapse_spaces(value)


def _clean_bullet(value: str) -> str:
    cleaned = _normalize_text(value)
    cleaned = re.sub(r"^[\-\*•\u2022\u00b7\u25aa\u25cf\u25e6]+\s*", "", cleaned).strip()
    return cleaned


def _normalize_date_token(value: Any) -> str:
    raw = _normalize_text(value)
    return raw


def _strip_environment_skill_lines(text: str) -> str:
    """Remove Environment:/Tools:/Technologies: lines — those belong in Skills, not work description."""
    if not text or not isinstance(text, str):
        return text
    lines = text.splitlines()
    kept: list[str] = []
    for ln in lines:
        stripped = ln.strip()
        if ENVIRONMENT_LINE_RE.match(stripped):
            continue
        kept.append(ln)
    return "\n".join(kept).strip()


def _normalize_description(value: Any) -> str:
    raw = _normalize_text(value)
    if not raw:
        return ""
    raw = _strip_environment_skill_lines(raw)
    raw = re.sub(r"(?m)^\|\s*", "", raw)
    raw = re.sub(r"\s*\|\s*", " - ", raw)
    raw = _collapse_spaces(raw)
    return raw


def _is_placeholder(value: Any) -> bool:
    cleaned = _normalize_text(value).lower()
    if not cleaned:
        return False
    return bool(_PLACEHOLDER_RE.match(cleaned))


def _is_skillish(value: Any) -> bool:
    cleaned = _normalize_text(value)
    if not cleaned:
        return False
    return WorkExperienceParser._looks_like_skillish_header(cleaned)


def _has_any_date(entry: dict[str, Any]) -> bool:
    return bool(_normalize_date_token(entry.get("start_date")) or _normalize_date_token(entry.get("end_date")))


def _has_any_body(entry: dict[str, Any]) -> bool:
    bullets = entry.get("bullets")
    if isinstance(bullets, list):
        if any(_clean_bullet(b) for b in bullets if isinstance(b, str)):
            return True
    if _normalize_description(entry.get("description")):
        return True
    return False


def _get_title(entry: dict[str, Any]) -> str:
    """Extract title from entry, checking role/job_title/designation as fallbacks."""
    return _normalize_text(
        entry.get("title") or entry.get("role") or entry.get("job_title") or entry.get("designation")
    )


def _merge_entries(primary: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    out = dict(primary)

    for key in ("company", "client", "location", "employment_type"):
        if not _normalize_text(out.get(key)) and _normalize_text(incoming.get(key)):
            out[key] = _normalize_text(incoming.get(key))
    # Title: also check role, job_title, designation
    if not _get_title(out) and _get_title(incoming):
        out["title"] = _get_title(incoming)

    out["is_current"] = bool(out.get("is_current")) or bool(incoming.get("is_current"))

    if not _normalize_date_token(out.get("start_date")) and _normalize_date_token(incoming.get("start_date")):
        out["start_date"] = _normalize_date_token(incoming.get("start_date"))
    if not _normalize_date_token(out.get("end_date")) and _normalize_date_token(incoming.get("end_date")):
        out["end_date"] = _normalize_date_token(incoming.get("end_date"))

    p_desc = _normalize_description(out.get("description"))
    i_desc = _normalize_description(incoming.get("description"))
    if i_desc and (not p_desc or len(i_desc) > len(p_desc)):
        out["description"] = i_desc

    merged_bullets: list[str] = []
    seen: set[str] = set()

    def _add_bullets(items: Any) -> None:
        if not isinstance(items, list):
            return
        for b in items:
            if not isinstance(b, str):
                continue
            cleaned = _clean_bullet(b)
            if not cleaned:
                continue
            key = cleaned.lower()
            if key in seen:
                continue
            seen.add(key)
            merged_bullets.append(cleaned)

    _add_bullets(primary.get("bullets"))
    _add_bullets(incoming.get("bullets"))
    out["bullets"] = merged_bullets

    try:
        p_conf = float(out.get("confidence", 0.0) or 0.0)
    except (TypeError, ValueError):
        p_conf = 0.0
    try:
        i_conf = float(incoming.get("confidence", 0.0) or 0.0)
    except (TypeError, ValueError):
        i_conf = 0.0
    out["confidence"] = max(p_conf, i_conf)

    return out


def _count_filled_fields(entry: dict[str, Any]) -> int:
    """Score entry by number of filled fields (prefer description/bullets)."""
    score = 0
    if _normalize_description(entry.get("description")):
        score += 10
    bullets = entry.get("bullets")
    if isinstance(bullets, list):
        score += len([b for b in bullets if isinstance(b, str) and _clean_bullet(b)])
    if _normalize_date_token(entry.get("end_date")):
        score += 2
    if _normalize_text(entry.get("client")):
        score += 1
    if _normalize_text(entry.get("location")):
        score += 1
    if _normalize_text(entry.get("employment_type")):
        score += 1
    return score


def deduplicate_work_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Remove duplicate work entries. Two entries are duplicates if
    company + job_title + start_date match. Keep the entry with more filled fields.
    """
    if not isinstance(entries, list) or not entries:
        return list(entries) if isinstance(entries, list) else []

    seen: dict[tuple[str, str, str], dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        company = _normalize_text(entry.get("company")).lower()
        title = _normalize_text(entry.get("title")).lower()
        start_date = _normalize_date_token(entry.get("start_date")).lower()
        key = (company, title, start_date)

        if key not in seen:
            seen[key] = entry
            continue

        existing = seen[key]
        if _count_filled_fields(entry) > _count_filled_fields(existing):
            seen[key] = entry

    result = list(seen.values())
    removed = len(entries) - len(result)
    if removed > 0:
        logger.info("deduplicate_work_entries removed %d duplicate(s)", removed)
    return result


def sanitize_work_experience_entries(entries: Any) -> list[dict[str, Any]]:
    if not isinstance(entries, list) or not entries:
        return []

    cleaned: list[dict[str, Any]] = []
    for item in entries:
        if not isinstance(item, dict):
            continue

        company = _clean_company_name(_normalize_text(item.get("company")))
        title_raw = _normalize_text(item.get("title") or item.get("role") or item.get("job_title") or item.get("designation"))
        # Reject locations mistakenly stored as titles (e.g. "Minneapolis, Mn")
        if title_raw and _LOCATION_AS_TITLE_RE.match(title_raw.strip()):
            title_raw = ""
        title = title_raw
        # Use client as company when company is empty (e.g. "CLIENT: Home Depot" format)
        if not company:
            company = _clean_company_name(_normalize_text(item.get("client")))

        if not company and not title:
            continue

        if _is_placeholder(company) or _is_placeholder(title):
            continue

        if _is_skillish(company) or _is_skillish(title):
            continue

        if len(company) > 180 or len(title) > 180:
            continue

        normalized: dict[str, Any] = dict(item)
        normalized["company"] = company or None
        normalized["title"] = title or None
        normalized["client"] = _normalize_text(item.get("client")) or None
        normalized["location"] = _normalize_text(item.get("location")) or None
        normalized["employment_type"] = _normalize_text(item.get("employment_type")) or None
        normalized["start_date"] = _normalize_date_token(item.get("start_date")) or None
        normalized["end_date"] = _normalize_date_token(item.get("end_date")) or None
        normalized["description"] = _normalize_description(item.get("description")) or None
        normalized["is_current"] = bool(item.get("is_current", False))

        bullets_raw = item.get("bullets")
        bullets_out: list[str] = []
        if isinstance(bullets_raw, list):
            for b in bullets_raw:
                if not isinstance(b, str):
                    continue
                bb = _clean_bullet(b)
                if bb and not ENVIRONMENT_LINE_RE.match(bb):
                    bullets_out.append(bb)
        normalized["bullets"] = bullets_out

        company = str(normalized.get("company") or "").strip()
        title = str(normalized.get("title") or "").strip()
        has_date = _has_any_date(normalized)
        has_body = _has_any_body(normalized)

        # Drop only if we have nothing at all
        if not company and not title and not has_date and not has_body:
            continue

        # Allow through if company+title exist, even without date/body
        if not has_date and not has_body:
            if not company or not title:
                continue
            normalized["_needs_review"] = True  # flag for QA but keep it

        cleaned.append(normalized)

    deduped: dict[tuple[str, str, str, str, str, bool], dict[str, Any]] = {}
    order: list[tuple[str, str, str, str, str, bool]] = []

    for entry in cleaned:
        key = (
            _normalize_text(entry.get("company")).lower(),
            _normalize_text(entry.get("title")).lower(),
            _normalize_text(entry.get("client")).lower(),
            _normalize_date_token(entry.get("start_date")).lower(),
            _normalize_date_token(entry.get("end_date")).lower(),
            bool(entry.get("is_current")),
        )

        if key not in deduped:
            deduped[key] = entry
            order.append(key)
            continue

        deduped[key] = _merge_entries(deduped[key], entry)

    merged_list = [deduped[k] for k in order]
    return deduplicate_work_entries(merged_list)
