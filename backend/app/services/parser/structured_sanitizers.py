from __future__ import annotations

import re
from typing import Any

from app.services.parser.skill_extractor import map_category_to_master


_PLACEHOLDER_TOKEN_RE = re.compile(
    r"^(n/a|na\b|none|null|unknown|tbd|tbc|school|university|college|institute|degree|major|certification|certificate|issuer|provider)$",
    re.IGNORECASE,
)


def _collapse_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _norm_str(value: Any) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        value = str(value)
    return _collapse_spaces(value)


def _is_placeholder(value: Any) -> bool:
    cleaned = _norm_str(value)
    if not cleaned:
        return False
    return bool(_PLACEHOLDER_TOKEN_RE.match(cleaned))


def sanitize_education_entries(entries: Any) -> list[dict[str, Any]]:
    if entries is None:
        return []
    if isinstance(entries, dict):
        entries = [entries]
    if not isinstance(entries, list) or not entries:
        return []

    cleaned: list[dict[str, Any]] = []
    for item in entries:
        if not isinstance(item, dict):
            continue

        institution = _norm_str(item.get("institution"))
        degree = _norm_str(item.get("degree"))
        field = _norm_str(item.get("field_of_study"))

        if _is_placeholder(institution):
            institution = ""
        if _is_placeholder(degree):
            degree = ""
        if _is_placeholder(field):
            field = ""

        if not (institution or degree or field):
            continue

        out = dict(item)
        out["institution"] = institution or None
        out["degree"] = degree or None
        out["field_of_study"] = field or None

        honors = _norm_str(item.get("honors"))
        out["honors"] = honors or None

        desc = _norm_str(item.get("description"))
        if desc and not out.get("honors"):
            out["honors"] = desc

        cleaned.append(out)

    deduped: dict[tuple[str, str, str, str, str], dict[str, Any]] = {}
    order: list[tuple[str, str, str, str, str]] = []

    for e in cleaned:
        key = (
            _norm_str(e.get("institution")).lower(),
            _norm_str(e.get("degree")).lower(),
            _norm_str(e.get("field_of_study")).lower(),
            _norm_str(e.get("start_date")).lower(),
            _norm_str(e.get("end_date")).lower(),
        )
        if key not in deduped:
            deduped[key] = e
            order.append(key)
            continue

        existing = deduped[key]
        if not _norm_str(existing.get("honors")) and _norm_str(e.get("honors")):
            existing["honors"] = _norm_str(e.get("honors"))
        if not _norm_str(existing.get("gpa")) and _norm_str(e.get("gpa")):
            existing["gpa"] = e.get("gpa")

        deduped[key] = existing

    return [deduped[k] for k in order]


_CERT_BAD_RE = re.compile(
    r"\b(responsibilities|experience|skills|project|projects|developed|built|designed)\b",
    re.IGNORECASE,
)


def sanitize_certifications_entries(entries: Any) -> list[dict[str, Any]]:
    if not isinstance(entries, list) or not entries:
        return []

    cleaned: list[dict[str, Any]] = []
    for item in entries:
        if not isinstance(item, dict):
            continue

        name = _norm_str(item.get("name"))
        if not name:
            continue
        if len(name) > 200:
            continue
        if _CERT_BAD_RE.search(name):
            continue

        org = _norm_str(item.get("issuing_organization") or item.get("issuer") or item.get("provider"))
        if _is_placeholder(org):
            org = ""
        if len(org) > 200:
            org = org[:200]

        cred = _norm_str(item.get("credential_id"))
        if len(cred) > 100:
            cred = cred[:100]

        out = dict(item)
        out["name"] = name
        out["issuing_organization"] = org or None
        out["credential_id"] = cred or None
        cleaned.append(out)

    deduped: dict[tuple[str, str, str, str, str], dict[str, Any]] = {}
    order: list[tuple[str, str, str, str, str]] = []

    for e in cleaned:
        key = (
            _norm_str(e.get("name")).lower(),
            _norm_str(e.get("issuing_organization")).lower(),
            _norm_str(e.get("credential_id")).lower(),
            _norm_str(e.get("issue_date")).lower(),
            _norm_str(e.get("expiry_date")).lower(),
        )
        if key not in deduped:
            deduped[key] = e
            order.append(key)
            continue

        existing = deduped[key]
        if not _norm_str(existing.get("issuing_organization")) and _norm_str(e.get("issuing_organization")):
            existing["issuing_organization"] = _norm_str(e.get("issuing_organization"))
        if not _norm_str(existing.get("credential_id")) and _norm_str(e.get("credential_id")):
            existing["credential_id"] = _norm_str(e.get("credential_id"))
        deduped[key] = existing

    return [deduped[k] for k in order]


_SKILL_BAD_RE = re.compile(r"\b(developed|built|designed|implemented|responsibilities)\b", re.IGNORECASE)


def sanitize_skill_entries(entries: Any) -> list[dict[str, Any]]:
    if not isinstance(entries, list) or not entries:
        return []

    cleaned: list[dict[str, Any]] = []
    for item in entries:
        if not isinstance(item, dict):
            continue

        name = _norm_str(item.get("name"))
        if not name:
            continue
        if len(name) > 150:
            continue
        if _SKILL_BAD_RE.search(name):
            continue
        if "," in name and len(name) <= 120:
            continue

        normalized = _norm_str(item.get("normalized_name"))
        normalized = (normalized.lower() if normalized else "") or " ".join((name or "").strip().lower().split())

        out = dict(item)
        out["name"] = name
        out["normalized_name"] = normalized or None
        category = _norm_str(item.get("category"))
        category_mapped = map_category_to_master(category) if category else None
        out["category"] = (category_mapped[:100] if category_mapped else None)
        cleaned.append(out)

    deduped: dict[str, dict[str, Any]] = {}
    order: list[str] = []

    for e in cleaned:
        key = (_norm_str(e.get("normalized_name")) or _norm_str(e.get("name"))).lower()
        if not key:
            continue
        if key not in deduped:
            deduped[key] = e
            order.append(key)
            continue

        existing = deduped[key]
        if not _norm_str(existing.get("normalized_name")) and _norm_str(e.get("normalized_name")):
            existing["normalized_name"] = _norm_str(e.get("normalized_name")).lower()
        if not _norm_str(existing.get("category")) and _norm_str(e.get("category")):
            existing["category"] = _norm_str(e.get("category"))[:100]
        deduped[key] = existing

    return [deduped[k] for k in order]
