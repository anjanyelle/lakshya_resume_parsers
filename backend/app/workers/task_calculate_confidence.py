from __future__ import annotations

import re
from typing import Any

from app.core.observability import EXPERIENCE_PARSE_QUALITY_SCORE, RESUME_PARSE_QUALITY_SCORE


_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
_E164_RE = re.compile(r"^\+[1-9]\d{7,14}$")
_PHONE_RE = re.compile(r"\+?\d[\d\s().-]{7,}\d")


def _clamp(v: float) -> float:
    return max(0.0, min(1.0, float(v)))


def _cap_words_score(name: str) -> float:
    tokens = [t for t in re.split(r"\s+", name.strip()) if t]
    if not tokens:
        return 0.0
    cap_words = sum(1 for t in tokens if t[:1].isupper() and t[1:].islower())
    if len(tokens) >= 2 and cap_words >= 2:
        return 0.95
    if len(tokens) == 1:
        return 0.6
    return 0.7


def build_per_field_confidence(parsed: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], list[str]]:
    sections = parsed.get("sections") if isinstance(parsed.get("sections"), dict) else {}
    contact = parsed.get("contact") if isinstance(parsed.get("contact"), dict) else {}
    debug = parsed.get("debug") if isinstance(parsed.get("debug"), dict) else {}

    fields: dict[str, dict[str, Any]] = {}

    name_val = ""
    if isinstance(contact.get("name"), dict):
        name_val = str(contact.get("name", {}).get("name") or "").strip()
    if name_val:
        score = _cap_words_score(name_val)
        reason = "two_capitalized_words" if score >= 0.9 else "single_word_or_mixed"
    else:
        score = 0.0
        reason = "missing"
    fields["name"] = {"score": float(score), "reason": reason}

    email_val = ""
    emails = contact.get("emails") if isinstance(contact.get("emails"), list) else []
    for e in emails:
        if isinstance(e, dict) and str(e.get("email") or "").strip():
            email_val = str(e.get("email") or "").strip()
            break
    if email_val and _EMAIL_RE.match(email_val):
        fields["email"] = {"score": 1.0, "reason": "valid_email_regex"}
    else:
        fields["email"] = {"score": 0.0, "reason": "missing_or_invalid"}

    phone_val = ""
    phones = contact.get("phones") if isinstance(contact.get("phones"), list) else []
    for p in phones:
        if isinstance(p, dict) and str(p.get("phone") or "").strip():
            phone_val = str(p.get("phone") or "").strip()
            break
    if phone_val and _E164_RE.match(phone_val):
        fields["phone"] = {"score": 1.0, "reason": "e164_normalized"}
    elif phone_val and _PHONE_RE.search(phone_val):
        fields["phone"] = {"score": 0.7, "reason": "raw_pattern_match"}
    else:
        fields["phone"] = {"score": 0.0, "reason": "missing"}

    loc_score = 0.0
    loc_reason = "missing"
    location = contact.get("location") if isinstance(contact.get("location"), dict) else {}
    if any(str(location.get(k) or "").strip() for k in ("city", "country")):
        loc_score = 0.6
        loc_reason = "city_country_pattern"
    fields["location"] = {"score": float(loc_score), "reason": loc_reason}

    summary_block = sections.get("summary") if isinstance(sections, dict) else None
    summary_conf = 0.0
    if isinstance(summary_block, dict):
        try:
            summary_conf = float(summary_block.get("confidence", 0.0) or 0.0)
        except (TypeError, ValueError):
            summary_conf = 0.0
    fields["summary"] = {
        "score": _clamp(summary_conf),
        "reason": f"section_confidence_{_clamp(summary_conf):.2f}",
    }

    years_val = parsed.get("total_experience_years")
    try:
        years = float(years_val) if years_val is not None else None
    except (TypeError, ValueError):
        years = None
    if years is None:
        fields["total_experience_years"] = {"score": 0.0, "reason": "missing"}
    else:
        fields["total_experience_years"] = {"score": 0.8, "reason": "computed_from_dates"}

    work_debug = debug.get("work_experience") if isinstance(debug.get("work_experience"), dict) else {}
    quality = work_debug.get("primary_quality_score")
    try:
        q = float(quality) if quality is not None else None
    except (TypeError, ValueError):
        q = None
    if q is None:
        fields["work_experience"] = {"score": 0.0, "reason": "missing_quality_score"}
    else:
        score = _clamp(q / 2.0)
        fields["work_experience"] = {"score": float(score), "reason": f"quality_score_{score:.2f}"}

    edu_items = parsed.get("education") if isinstance(parsed.get("education"), list) else []
    if not edu_items:
        fields["education"] = {"score": 0.0, "reason": "missing"}
    else:
        per: list[float] = []
        for e in edu_items:
            if not isinstance(e, dict):
                continue
            inst_ok = bool(str(e.get("institution") or "").strip())
            degree_ok = bool(str(e.get("degree") or "").strip())
            year_ok = bool(str(e.get("end_date") or e.get("graduation_year") or "").strip())
            per.append((int(inst_ok) + int(degree_ok) + int(year_ok)) / 3.0)
        base = (sum(per) / len(per)) if per else 0.0
        score = _clamp(base * 0.9)
        fields["education"] = {"score": float(score), "reason": "degree_institution_date_present"}

    skills_items = parsed.get("skills") if isinstance(parsed.get("skills"), list) else []
    skill_count = len([s for s in skills_items if isinstance(s, dict) and str(s.get("name") or s.get("normalized_name") or "").strip()])
    skill_score = _clamp(skill_count / 10.0)
    fields["skills"] = {"score": float(skill_score), "reason": f"skill_count_{skill_count}"}

    cert_items = parsed.get("certifications") if isinstance(parsed.get("certifications"), list) else []
    cert_count = len([c for c in cert_items if isinstance(c, dict) and str(c.get("name") or "").strip()])
    if cert_count <= 0:
        fields["certifications"] = {"score": 0.0, "reason": "cert_count_0"}
    else:
        score = _clamp((cert_count / 3.0) * 0.8)
        fields["certifications"] = {"score": float(score), "reason": f"cert_count_{cert_count}"}

    work_items = parsed.get("work_experience") if isinstance(parsed.get("work_experience"), list) else []
    client_conf = ""
    for w in work_items:
        if not isinstance(w, dict):
            continue
        if str(w.get("client") or "").strip():
            client_conf = str(w.get("client_confidence") or "").strip().lower()
            if client_conf:
                break
    if client_conf == "high":
        fields["client_names"] = {"score": 0.8, "reason": "deterministic_pattern_high"}
    elif client_conf == "medium":
        fields["client_names"] = {"score": 0.5, "reason": "deterministic_pattern_medium"}
    else:
        fields["client_names"] = {"score": 0.0, "reason": "not_extracted"}

    weakest_fields = [k for k, v in fields.items() if float(v.get("score", 0.0) or 0.0) < 0.6]
    return fields, weakest_fields


def record_quality_metrics(*, filename: str | None, parsed: dict[str, Any], overall_score: float) -> None:
    file_type = "unknown"
    try:
        if filename and "." in filename:
            file_type = filename.rsplit(".", 1)[-1].lower()
    except Exception:
        file_type = "unknown"

    try:
        RESUME_PARSE_QUALITY_SCORE.labels(file_type=file_type).observe(float(overall_score))
    except Exception:
        pass

    try:
        we_debug = parsed.get("debug") if isinstance(parsed.get("debug"), dict) else {}
        we_block = we_debug.get("work_experience") if isinstance(we_debug.get("work_experience"), dict) else {}
        q_raw = we_block.get("primary_quality_score")
        q_val = float(q_raw) if q_raw is not None else None
    except Exception:
        q_val = None
    if q_val is not None:
        try:
            EXPERIENCE_PARSE_QUALITY_SCORE.observe(max(0.0, min(1.0, float(q_val) / 2.0)))
        except Exception:
            pass
