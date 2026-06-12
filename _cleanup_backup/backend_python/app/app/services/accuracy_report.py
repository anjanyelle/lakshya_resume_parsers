"""Accuracy report service for resume parser evaluation against ground truth fixtures."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable

import dateparser

from app.services.parser.certification_parser import CertificationParser
from app.services.parser.contact_extractor import ContactExtractor
from app.services.parser.education_parser import EducationParser
from app.services.parser.extract_text import extract_text
from app.services.parser.section_boundary_extractor import extract_certifications
from app.services.parser.section_parser import SectionParser
from app.services.parser.skill_extractor import SkillExtractor
from app.services.parser.work_experience_parser import WorkExperienceParser


def _collapse_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _normalize_string(value: Any) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        value = str(value)
    return _collapse_spaces(value).lower()


def _normalize_date(value: Any) -> str:
    if value is None:
        return ""
    raw = str(value).strip()
    if not raw:
        return ""
    if re.fullmatch(r"\d{4}-\d{2}", raw):
        return raw
    dt = dateparser.parse(raw)
    if not dt:
        return _normalize_string(raw)
    return dt.strftime("%Y-%m")


def _normalize_skill(value: Any) -> str:
    if isinstance(value, dict):
        raw = value.get("normalized_name") or value.get("name") or ""
    else:
        raw = value
    return _normalize_string(raw)


@dataclass(frozen=True)
class PRF1:
    precision: float
    recall: float
    f1: float


@dataclass(frozen=True)
class AccuracyReport:
    """Aggregated accuracy metrics for the resume parser."""

    section_found_rate: float
    section_bleed_rate: float
    contact_accuracy: float
    work_accuracy: float
    work_company_f1: PRF1
    work_title_f1: PRF1
    work_dates_accuracy: float
    work_date_extraction_rate: float
    work_entry_count_diff: float
    skills_f1: PRF1
    education_f1: PRF1
    certifications_f1: PRF1
    overall: float
    case_count: int
    case_rows: list[dict[str, Any]]


def _format_date_ym(d: date | None) -> str | None:
    if not d:
        return None
    return d.strftime("%Y-%m")


def _normalize_lines(value: str) -> list[str]:
    if not value:
        return []
    out: list[str] = []
    for ln in value.splitlines():
        n = _normalize_string(ln)
        if n:
            out.append(n)
    return out


def _normalize_truth(truth: dict[str, Any]) -> dict[str, Any]:
    """Normalize truth payload from various formats to standard format."""
    out: dict[str, Any] = {}
    contact = truth.get("contact")
    if isinstance(contact, dict):
        name_val = contact.get("full_name") or (
            contact.get("name", {}).get("name") if isinstance(contact.get("name"), dict) else None
        )
        email_val = contact.get("email")
        if email_val is None and isinstance(contact.get("emails"), list) and contact["emails"]:
            email_val = contact["emails"][0].get("email") if isinstance(contact["emails"][0], dict) else None
        phone_val = contact.get("phone")
        if phone_val is None and isinstance(contact.get("phones"), list) and contact["phones"]:
            phone_val = contact["phones"][0].get("phone") if isinstance(contact["phones"][0], dict) else None
        loc = contact.get("location")
        if isinstance(loc, dict):
            parts = [loc.get("city"), loc.get("state"), loc.get("country")]
            location_val = ", ".join(p for p in parts if isinstance(p, str) and p.strip()) or None
        else:
            location_val = contact.get("location")
        out["contact"] = {
            "full_name": name_val,
            "email": email_val,
            "phone": phone_val,
            "linkedin_url": contact.get("linkedin_url"),
            "location": location_val,
        }
    work_raw = truth.get("work_history") or truth.get("work_experience") or []
    if isinstance(work_raw, list):
        out["work_history"] = []
        for j in work_raw:
            if not isinstance(j, dict):
                continue
            out["work_history"].append({
                "company_name": j.get("company_name") or j.get("company"),
                "client_name": j.get("client_name") or j.get("client"),
                "job_title": j.get("job_title") or j.get("title"),
                "start_date": j.get("start_date"),
                "end_date": j.get("end_date"),
            })
    edu_raw = truth.get("education") or []
    if isinstance(edu_raw, list):
        out["education"] = [e for e in edu_raw if isinstance(e, dict)]
    cert_raw = truth.get("certifications") or []
    if isinstance(cert_raw, list):
        out["certifications"] = [c for c in cert_raw if isinstance(c, dict)]
    skills_raw = truth.get("skills") or []
    if isinstance(skills_raw, list):
        out["skills"] = []
        for s in skills_raw:
            if isinstance(s, dict):
                val = s.get("normalized_name") or s.get("name") or ""
            elif isinstance(s, str):
                val = s
            else:
                continue
            if val:
                out["skills"].append(val)
    return out


def _iter_cases(fixtures_dir: Path) -> Iterable[tuple[str, Path, Path]]:
    if not fixtures_dir.exists():
        return
    for case_dir in sorted(fixtures_dir.iterdir()):
        if not case_dir.is_dir():
            continue
        expected_path = case_dir / "expected.json"
        if not expected_path.exists():
            expected_path = case_dir / "truth.json"
        if not expected_path.exists():
            continue
        preferred = [
            case_dir / "resume.pdf",
            case_dir / "resume.docx",
            case_dir / "resume.doc",
        ]
        resume_path = next((p for p in preferred if p.exists()), None)
        if resume_path is None:
            originals = list(case_dir.glob("original.*"))
            resume_path = originals[0] if len(originals) == 1 else None
        if resume_path is None:
            continue
        yield case_dir.name, resume_path, expected_path


def _parse_resume(file_path: Path) -> dict[str, Any]:
    extracted = extract_text(file_path)
    raw_text = extracted.text

    section_parser = SectionParser(use_spacy=True)
    sections = section_parser.parse(raw_text)

    contact_extractor = ContactExtractor()
    contact = contact_extractor.extract_all(raw_text)

    experience_text = raw_text
    exp_section = sections.get("experience")
    if exp_section is not None and getattr(exp_section, "content", ""):
        experience_text = exp_section.content

    work_parser = WorkExperienceParser()
    jobs = work_parser.parse_experience_section(experience_text)

    education_text = raw_text
    edu_section = sections.get("education")
    if edu_section is not None and getattr(edu_section, "content", ""):
        education_text = edu_section.content
    education_entries = EducationParser().parse(education_text)

    cert_text = ""
    boundary = extract_certifications(raw_text)
    if getattr(boundary, "section_found", False) and getattr(boundary, "content", ""):
        cert_text = boundary.content
    else:
        cert_section = sections.get("certifications")
        if cert_section is not None and getattr(cert_section, "content", ""):
            cert_text = cert_section.content
    certifications = CertificationParser().parse(cert_text) if cert_text.strip() else []

    skills_text = ""
    skills_conf = None
    skills_section = sections.get("skills")
    if skills_section is not None and getattr(skills_section, "content", ""):
        skills_text = skills_section.content
        try:
            skills_conf = float(getattr(skills_section, "confidence", 0.0) or 0.0)
        except (TypeError, ValueError):
            skills_conf = None

    skill_extractor = SkillExtractor()
    skill_matches = skill_extractor.extract_all(
        skills_text,
        jobs,
        skills_section_confidence=skills_conf,
        raw_text=raw_text,
    )

    def _first_email() -> str | None:
        return contact.emails[0].email if contact.emails else None

    def _first_phone() -> str | None:
        return contact.phones[0].phone if contact.phones else None

    linkedin = None
    try:
        linkedin = contact.urls.linkedin.url if contact.urls and contact.urls.linkedin else None
    except Exception:
        linkedin = None

    location = None
    try:
        parts = [
            getattr(contact.location, "city", None),
            getattr(contact.location, "state", None),
            getattr(contact.location, "country", None),
        ]
        parts = [p for p in parts if isinstance(p, str) and p.strip()]
        location = ", ".join(parts) if parts else None
    except Exception:
        location = None

    return {
        "sections": {
            key: {
                "content": getattr(value, "content", ""),
                "confidence": getattr(value, "confidence", 0.0),
            }
            for key, value in sections.items()
        },
        "contact": {
            "full_name": getattr(contact.name, "name", None),
            "email": _first_email(),
            "phone": _first_phone(),
            "linkedin_url": linkedin,
            "location": location,
        },
        "work_history": [
            {
                "company_name": j.company,
                "client_name": j.client,
                "job_title": j.title,
                "start_date": _format_date_ym(j.start_date),
                "end_date": _format_date_ym(j.end_date),
                "is_current": bool(j.is_current),
                "location": j.location,
                "bullets": list(j.bullets or []),
                "description": j.description,
                "confidence": j.confidence,
            }
            for j in jobs
        ],
        "education": [
            {
                "institution": e.institution,
                "degree": e.degree,
                "field_of_study": e.field_of_study,
                "start_date": _format_date_ym(e.start_date),
                "end_date": _format_date_ym(e.end_date),
                "in_progress": bool(e.in_progress),
                "confidence": e.confidence,
            }
            for e in education_entries
        ],
        "certifications": [
            {
                "name": c.name,
                "issuing_organization": c.issuing_organization,
                "issue_date": _format_date_ym(c.issue_date),
                "expiry_date": _format_date_ym(c.expiry_date),
                "credential_id": c.credential_id,
                "credential_url": c.credential_url,
                "confidence": c.confidence,
            }
            for c in certifications
        ],
        "skills": [m.__dict__ for m in skill_matches],
    }


def _prf1(tp: int, fp: int, fn: int) -> PRF1:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
    return PRF1(precision=precision, recall=recall, f1=f1)


def _score_contact(truth: dict[str, Any], pred: dict[str, Any]) -> float:
    t = truth.get("contact") if isinstance(truth.get("contact"), dict) else truth
    p = pred.get("contact") if isinstance(pred.get("contact"), dict) else pred
    fields = ["full_name", "email", "phone", "linkedin_url", "location"]

    def _eq(field: str) -> bool:
        tv = t.get(field)
        pv = p.get(field)
        return _normalize_string(tv) == _normalize_string(pv)

    matches = sum(1 for f in fields if _eq(f))
    return matches / len(fields)


def _score_work(truth: dict[str, Any], pred: dict[str, Any]) -> float:
    truth_jobs = truth.get("work_history") if isinstance(truth.get("work_history"), list) else []
    pred_jobs = pred.get("work_history") if isinstance(pred.get("work_history"), list) else []

    if not truth_jobs:
        return 1.0 if not pred_jobs else 0.0

    remaining = [j for j in pred_jobs if isinstance(j, dict)]
    per_truth: list[float] = []

    def _job_score(tj: dict[str, Any], pj: dict[str, Any]) -> float:
        fields = ["company_name", "client_name", "job_title", "start_date", "end_date"]
        ok = 0
        for f in fields:
            tv = tj.get(f)
            pv = pj.get(f)
            if f in {"start_date", "end_date"}:
                ok += int(_normalize_date(tv) == _normalize_date(pv))
            else:
                ok += int(_normalize_string(tv) == _normalize_string(pv))
        return ok / len(fields)

    for tj in truth_jobs:
        if not isinstance(tj, dict):
            continue
        if not remaining:
            per_truth.append(0.0)
            continue
        best_idx = 0
        best = -1.0
        for idx, pj in enumerate(remaining):
            score = _job_score(tj, pj)
            if score > best:
                best = score
                best_idx = idx
        per_truth.append(max(best, 0.0))
        remaining.pop(best_idx)

    return sum(per_truth) / len(per_truth) if per_truth else 0.0


def _extract_section_texts(payload: dict[str, Any]) -> dict[str, str]:
    raw = payload.get("sections")
    if not isinstance(raw, dict):
        return {}
    out: dict[str, str] = {}
    for k, v in raw.items():
        if not isinstance(k, str):
            continue
        if isinstance(v, dict):
            out[k] = str(v.get("content") or "")
            continue
        out[k] = str(getattr(v, "content", "") or "")
    return out


def _score_section_found_rate(pred: dict[str, Any]) -> float:
    sections = _extract_section_texts(pred)
    keys = ["summary", "experience", "education", "skills", "certifications", "projects"]
    found = 0
    for k in keys:
        content = str(sections.get(k) or "").strip()
        if content:
            found += 1
    return found / len(keys)


def _score_section_bleed_rate(pred: dict[str, Any]) -> float:
    sections = _extract_section_texts(pred)
    if not sections:
        return 0.0
    per_section: list[float] = []
    keys = [k for k in sections.keys() if str(sections.get(k) or "").strip()]
    for k in keys:
        this_lines = set(_normalize_lines(sections.get(k) or ""))
        if not this_lines:
            continue
        other_lines: set[str] = set()
        for ok in keys:
            if ok == k:
                continue
            other_lines |= set(_normalize_lines(sections.get(ok) or ""))
        if not other_lines:
            per_section.append(0.0)
            continue
        overlap = len(this_lines & other_lines)
        per_section.append(overlap / max(1, len(this_lines)))
    return (sum(per_section) / len(per_section)) if per_section else 0.0


def _score_work_company_title_f1(truth: dict[str, Any], pred: dict[str, Any]) -> tuple[PRF1, PRF1]:
    truth_jobs = truth.get("work_history") or []
    pred_jobs = pred.get("work_history") or []

    truth_companies = {
        _normalize_string(j.get("company_name"))
        for j in truth_jobs
        if isinstance(j, dict) and _normalize_string(j.get("company_name"))
    }
    pred_companies = {
        _normalize_string(j.get("company_name"))
        for j in pred_jobs
        if isinstance(j, dict) and _normalize_string(j.get("company_name"))
    }
    truth_titles = {
        _normalize_string(j.get("job_title"))
        for j in truth_jobs
        if isinstance(j, dict) and _normalize_string(j.get("job_title"))
    }
    pred_titles = {
        _normalize_string(j.get("job_title"))
        for j in pred_jobs
        if isinstance(j, dict) and _normalize_string(j.get("job_title"))
    }

    tp_c = len(truth_companies & pred_companies)
    fp_c = len(pred_companies - truth_companies)
    fn_c = len(truth_companies - pred_companies)
    tp_t = len(truth_titles & pred_titles)
    fp_t = len(pred_titles - truth_titles)
    fn_t = len(truth_titles - pred_titles)

    return _prf1(tp_c, fp_c, fn_c), _prf1(tp_t, fp_t, fn_t)


def _match_work_jobs(
    truth_jobs: list[dict[str, Any]],
    pred_jobs: list[dict[str, Any]],
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    remaining = [j for j in pred_jobs if isinstance(j, dict)]
    pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []

    def _match_score(tj: dict[str, Any], pj: dict[str, Any]) -> float:
        score = 0.0
        if _normalize_string(tj.get("company_name")) == _normalize_string(pj.get("company_name")):
            score += 0.6
        if _normalize_string(tj.get("job_title")) == _normalize_string(pj.get("job_title")):
            score += 0.3
        if _normalize_string(tj.get("client_name")) == _normalize_string(pj.get("client_name")):
            score += 0.1
        return score

    for tj in truth_jobs:
        if not isinstance(tj, dict):
            continue
        if not remaining:
            break
        best_idx = 0
        best = -1.0
        for idx, pj in enumerate(remaining):
            s = _match_score(tj, pj)
            if s > best:
                best = s
                best_idx = idx
        pairs.append((tj, remaining.pop(best_idx)))
    return pairs


def _score_work_dates(truth: dict[str, Any], pred: dict[str, Any]) -> float:
    truth_jobs = truth.get("work_history") or []
    pred_jobs = pred.get("work_history") or []
    truth_jobs = [j for j in truth_jobs if isinstance(j, dict)]
    pred_jobs = [j for j in pred_jobs if isinstance(j, dict)]
    if not truth_jobs:
        return 1.0
    pairs = _match_work_jobs(truth_jobs, pred_jobs)
    if not pairs:
        return 0.0
    total = 0
    ok = 0
    for tj, pj in pairs:
        total += 2
        ok += int(_normalize_date(tj.get("start_date")) == _normalize_date(pj.get("start_date")))
        ok += int(_normalize_date(tj.get("end_date")) == _normalize_date(pj.get("end_date")))
    return ok / total if total else 0.0


def _score_work_date_extraction_rate(pred: dict[str, Any]) -> float:
    pred_jobs = pred.get("work_history") or []
    pred_jobs = [j for j in pred_jobs if isinstance(j, dict)]
    if not pred_jobs:
        return 0.0
    with_date = sum(1 for j in pred_jobs if _normalize_date(j.get("start_date")))
    return with_date / len(pred_jobs)


def _score_work_entry_count_diff(truth: dict[str, Any], pred: dict[str, Any]) -> float:
    truth_jobs = truth.get("work_history") or []
    pred_jobs = pred.get("work_history") or []
    t = len([j for j in truth_jobs if isinstance(j, dict)])
    p = len([j for j in pred_jobs if isinstance(j, dict)])
    return abs(p - t) / max(1, t)


def _score_skills(truth: dict[str, Any], pred: dict[str, Any]) -> PRF1:
    truth_raw = truth.get("skills") or []
    pred_raw = pred.get("skills") or []

    truth_skills = {_normalize_skill(s) for s in truth_raw} if isinstance(truth_raw, list) else set()
    pred_skills = (
        {_normalize_skill(s) for s in pred_raw}
        if isinstance(pred_raw, list)
        else set()
    )
    truth_skills.discard("")
    pred_skills.discard("")

    tp = len(truth_skills & pred_skills)
    fp = len(pred_skills - truth_skills)
    fn = len(truth_skills - pred_skills)
    return _prf1(tp, fp, fn)


def _score_education(truth: dict[str, Any], pred: dict[str, Any]) -> PRF1:
    truth_raw = truth.get("education") or []
    pred_raw = pred.get("education") or []

    def _norm_item(item: dict[str, Any]) -> tuple[str, str, str, str, str]:
        return (
            _normalize_string(item.get("institution")),
            _normalize_string(item.get("degree")),
            _normalize_string(item.get("field_of_study")),
            _normalize_date(item.get("start_date")),
            _normalize_date(item.get("end_date")),
        )

    truth_set = {_norm_item(i) for i in truth_raw if isinstance(i, dict)} if isinstance(truth_raw, list) else set()
    pred_set = {_norm_item(i) for i in pred_raw if isinstance(i, dict)} if isinstance(pred_raw, list) else set()
    truth_set.discard(("", "", "", "", ""))
    pred_set.discard(("", "", "", "", ""))

    tp = len(truth_set & pred_set)
    fp = len(pred_set - truth_set)
    fn = len(truth_set - pred_set)
    return _prf1(tp, fp, fn)


def _score_certs(truth: dict[str, Any], pred: dict[str, Any]) -> PRF1:
    truth_raw = truth.get("certifications") or []
    pred_raw = pred.get("certifications") or []

    def _norm_item(item: dict[str, Any]) -> tuple[str, str, str, str]:
        return (
            _normalize_string(item.get("name")),
            _normalize_string(item.get("issuing_organization")),
            _normalize_date(item.get("issue_date")),
            _normalize_date(item.get("expiry_date")),
        )

    truth_set = {_norm_item(i) for i in truth_raw if isinstance(i, dict)} if isinstance(truth_raw, list) else set()
    pred_set = {_norm_item(i) for i in pred_raw if isinstance(i, dict)} if isinstance(pred_raw, list) else set()
    truth_set.discard(("", "", "", ""))
    pred_set.discard(("", "", "", ""))

    tp = len(truth_set & pred_set)
    fp = len(pred_set - truth_set)
    fn = len(truth_set - pred_set)
    return _prf1(tp, fp, fn)


def generate_accuracy_report(
    fixtures_dir: Path | None = None,
    output_path: Path | None = None,
) -> AccuracyReport:
    """
    Run accuracy evaluation against ground truth fixtures and return a report.

    Args:
        fixtures_dir: Directory containing resume fixtures (default: tests/fixtures/resumes).
        output_path: Optional path to write JSON report.

    Returns:
        AccuracyReport with aggregated metrics and per-case rows.
    """
    if fixtures_dir is None:
        fixtures_dir = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "resumes"

    case_rows: list[dict[str, Any]] = []
    section_found_rates: list[float] = []
    section_bleed_rates: list[float] = []
    contact_scores: list[float] = []
    work_scores: list[float] = []
    work_dates_scores: list[float] = []
    work_date_extract_scores: list[float] = []
    work_entry_count_diffs: list[float] = []
    work_company_f1s: list[PRF1] = []
    work_title_f1s: list[PRF1] = []
    skills_scores: list[PRF1] = []
    edu_scores: list[PRF1] = []
    cert_scores: list[PRF1] = []

    for case_id, resume_path, expected_path in _iter_cases(fixtures_dir):
        truth_payload = json.loads(expected_path.read_text(encoding="utf-8"))
        truth_payload = _normalize_truth(truth_payload)
        pred_payload = _parse_resume(resume_path)

        contact_acc = _score_contact(truth_payload, pred_payload)
        work_acc = _score_work(truth_payload, pred_payload)
        section_found = _score_section_found_rate(pred_payload)
        section_bleed = _score_section_bleed_rate(pred_payload)
        company_f1, title_f1 = _score_work_company_title_f1(truth_payload, pred_payload)
        dates_acc = _score_work_dates(truth_payload, pred_payload)
        date_extract = _score_work_date_extraction_rate(pred_payload)
        entry_diff = _score_work_entry_count_diff(truth_payload, pred_payload)
        skills_f1 = _score_skills(truth_payload, pred_payload)
        edu_f1 = _score_education(truth_payload, pred_payload)
        cert_f1 = _score_certs(truth_payload, pred_payload)

        section_found_rates.append(section_found)
        section_bleed_rates.append(section_bleed)
        contact_scores.append(contact_acc)
        work_scores.append(work_acc)
        work_company_f1s.append(company_f1)
        work_title_f1s.append(title_f1)
        work_dates_scores.append(dates_acc)
        work_date_extract_scores.append(date_extract)
        work_entry_count_diffs.append(entry_diff)
        skills_scores.append(skills_f1)
        edu_scores.append(edu_f1)
        cert_scores.append(cert_f1)

        case_rows.append({
            "id": case_id,
            "resume": resume_path.name,
            "section_found_rate": round(section_found, 4),
            "section_bleed_rate": round(section_bleed, 4),
            "contact_accuracy": round(contact_acc, 4),
            "work_accuracy": round(work_acc, 4),
            "work_company_f1": round(company_f1.f1, 4),
            "work_title_f1": round(title_f1.f1, 4),
            "work_dates_accuracy": round(dates_acc, 4),
            "work_date_extraction_rate": round(date_extract, 4),
            "work_entry_count_diff": round(entry_diff, 4),
            "skills_f1": round(skills_f1.f1, 4),
            "education_f1": round(edu_f1.f1, 4),
            "certifications_f1": round(cert_f1.f1, 4),
        })

    n = len(case_rows)

    def _avg(vals: Iterable[float]) -> float:
        vals = list(vals)
        return sum(vals) / len(vals) if vals else 0.0

    if n == 0:
        report = AccuracyReport(
            section_found_rate=0.0,
            section_bleed_rate=0.0,
            contact_accuracy=0.0,
            work_accuracy=0.0,
            work_company_f1=PRF1(0.0, 0.0, 0.0),
            work_title_f1=PRF1(0.0, 0.0, 0.0),
            work_dates_accuracy=0.0,
            work_date_extraction_rate=0.0,
            work_entry_count_diff=0.0,
            skills_f1=PRF1(0.0, 0.0, 0.0),
            education_f1=PRF1(0.0, 0.0, 0.0),
            certifications_f1=PRF1(0.0, 0.0, 0.0),
            overall=0.0,
            case_count=0,
            case_rows=[],
        )
    else:
        skills = PRF1(
            precision=_avg(s.precision for s in skills_scores),
            recall=_avg(s.recall for s in skills_scores),
            f1=_avg(s.f1 for s in skills_scores),
        )
        work_company = PRF1(
            precision=_avg(s.precision for s in work_company_f1s),
            recall=_avg(s.recall for s in work_company_f1s),
            f1=_avg(s.f1 for s in work_company_f1s),
        )
        work_title = PRF1(
            precision=_avg(s.precision for s in work_title_f1s),
            recall=_avg(s.recall for s in work_title_f1s),
            f1=_avg(s.f1 for s in work_title_f1s),
        )
        edu = PRF1(
            precision=_avg(s.precision for s in edu_scores),
            recall=_avg(s.recall for s in edu_scores),
            f1=_avg(s.f1 for s in edu_scores),
        )
        certs = PRF1(
            precision=_avg(s.precision for s in cert_scores),
            recall=_avg(s.recall for s in cert_scores),
            f1=_avg(s.f1 for s in cert_scores),
        )

        overall = (
            0.15 * _avg(section_found_rates)
            + 0.05 * (1.0 - _avg(section_bleed_rates))
            + 0.20 * _avg(contact_scores)
            + 0.20 * _avg(work_scores)
            + 0.10 * work_company.f1
            + 0.05 * work_title.f1
            + 0.10 * _avg(work_dates_scores)
            + 0.05 * _avg(work_date_extract_scores)
            + 0.05 * (1.0 - _avg(work_entry_count_diffs))
            + 0.03 * skills.f1
            + 0.01 * edu.f1
            + 0.01 * certs.f1
        )

        report = AccuracyReport(
            section_found_rate=_avg(section_found_rates),
            section_bleed_rate=_avg(section_bleed_rates),
            contact_accuracy=_avg(contact_scores),
            work_accuracy=_avg(work_scores),
            work_company_f1=work_company,
            work_title_f1=work_title,
            work_dates_accuracy=_avg(work_dates_scores),
            work_date_extraction_rate=_avg(work_date_extract_scores),
            work_entry_count_diff=_avg(work_entry_count_diffs),
            skills_f1=skills,
            education_f1=edu,
            certifications_f1=certs,
            overall=overall,
            case_count=n,
            case_rows=case_rows,
        )

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(_report_to_dict(report), indent=2),
            encoding="utf-8",
        )

    return report


def _report_to_dict(report: AccuracyReport) -> dict[str, Any]:
    return {
        "summary": {
            "case_count": report.case_count,
            "section_found_rate": round(report.section_found_rate, 4),
            "section_bleed_rate": round(report.section_bleed_rate, 4),
            "contact_accuracy": round(report.contact_accuracy, 4),
            "work_accuracy": round(report.work_accuracy, 4),
            "work_company_f1": round(report.work_company_f1.f1, 4),
            "work_title_f1": round(report.work_title_f1.f1, 4),
            "work_dates_accuracy": round(report.work_dates_accuracy, 4),
            "work_date_extraction_rate": round(report.work_date_extraction_rate, 4),
            "work_entry_count_diff": round(report.work_entry_count_diff, 4),
            "skills_f1": round(report.skills_f1.f1, 4),
            "education_f1": round(report.education_f1.f1, 4),
            "certifications_f1": round(report.certifications_f1.f1, 4),
            "overall": round(report.overall, 4),
        },
        "per_field": {
            "skills": {
                "precision": round(report.skills_f1.precision, 4),
                "recall": round(report.skills_f1.recall, 4),
                "f1": round(report.skills_f1.f1, 4),
            },
            "education": {
                "precision": round(report.education_f1.precision, 4),
                "recall": round(report.education_f1.recall, 4),
                "f1": round(report.education_f1.f1, 4),
            },
            "certifications": {
                "precision": round(report.certifications_f1.precision, 4),
                "recall": round(report.certifications_f1.recall, 4),
                "f1": round(report.certifications_f1.f1, 4),
            },
        },
        "cases": report.case_rows,
    }
