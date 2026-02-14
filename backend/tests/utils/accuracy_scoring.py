from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import dateparser
import phonenumbers


_CONTACT_WEIGHT = 0.40
_WORK_WEIGHT = 0.40
_SKILLS_WEIGHT = 0.20


@dataclass(frozen=True)
class SkillsF1:
    precision: float
    recall: float
    f1: float


@dataclass(frozen=True)
class ResumeScore:
    contact_accuracy: float
    work_accuracy: float
    skills_f1: SkillsF1
    overall: float


@dataclass(frozen=True)
class DatasetScore:
    contact_accuracy: float
    work_accuracy: float
    skills_f1: SkillsF1
    overall: float


def _collapse_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def normalize_string(value: Any) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        value = str(value)
    return _collapse_spaces(value).lower()


def normalize_email(value: Any) -> str:
    return normalize_string(value)


def _digits_only(value: str) -> str:
    return re.sub(r"\D+", "", value)


def normalize_phone(value: Any, default_region: str = "US") -> str:
    if value is None:
        return ""
    raw = str(value).strip()
    if not raw:
        return ""

    try:
        region = None if raw.startswith("+") else default_region
        number = phonenumbers.parse(raw, region)
        if phonenumbers.is_possible_number(number) and phonenumbers.is_valid_number(number):
            return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        pass

    return _digits_only(raw)


def normalize_date(value: Any) -> str:
    if value is None:
        return ""
    raw = str(value).strip()
    if not raw:
        return ""

    if re.fullmatch(r"\d{4}-\d{2}", raw):
        return raw

    dt = dateparser.parse(raw)
    if not dt:
        return normalize_string(raw)

    return dt.strftime("%Y-%m")


def normalize_skill(value: Any) -> str:
    if isinstance(value, dict):
        raw = value.get("normalized_name") or value.get("name") or ""
    else:
        raw = value
    return normalize_string(raw)


def _truthy_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _extract_personal_info(payload: dict[str, Any]) -> dict[str, Any]:
    personal_info = payload.get("personal_info")
    if isinstance(personal_info, dict):
        return personal_info

    structured = payload.get("structured_resume")
    if isinstance(structured, dict) and isinstance(structured.get("personal_info"), dict):
        return structured["personal_info"]

    return {}


def _extract_contact(payload: dict[str, Any]) -> dict[str, Any]:
    contact = payload.get("contact")
    return contact if isinstance(contact, dict) else {}


def _get_contact_value(payload: dict[str, Any], field_name: str) -> Any:
    personal = _extract_personal_info(payload)
    contact = _extract_contact(payload)

    if field_name == "full_name":
        return (
            personal.get("full_name")
            or _truthy_dict(contact.get("name")).get("name")
            or payload.get("full_name")
        )

    if field_name == "email":
        if personal.get("email"):
            return personal.get("email")
        emails = contact.get("emails")
        if isinstance(emails, list) and emails:
            first = emails[0]
            if isinstance(first, dict):
                return first.get("email")
            return first
        return payload.get("email")

    if field_name == "phone":
        if personal.get("phone"):
            return personal.get("phone")
        phones = contact.get("phones")
        if isinstance(phones, list) and phones:
            first = phones[0]
            if isinstance(first, dict):
                return first.get("phone")
            return first
        return payload.get("phone")

    if field_name == "linkedin_url":
        return (
            personal.get("linkedin")
            or _truthy_dict(_truthy_dict(contact.get("urls")).get("linkedin")).get("url")
            or _truthy_dict(contact.get("urls")).get("linkedin")
            or payload.get("linkedin_url")
            or payload.get("linkedin")
        )

    if field_name == "location":
        if personal.get("location"):
            return personal.get("location")
        location = contact.get("location")
        if isinstance(location, dict):
            city = location.get("city")
            state = location.get("state")
            country = location.get("country")
            parts = [p for p in [city, state, country] if isinstance(p, str) and p.strip()]
            if parts:
                return ", ".join(parts)
        return payload.get("location")

    raise ValueError(f"Unsupported contact field: {field_name}")


def _equal_strings(truth: Any, pred: Any) -> bool:
    return normalize_string(truth) == normalize_string(pred)


def _equal_emails(truth: Any, pred: Any) -> bool:
    return normalize_email(truth) == normalize_email(pred)


def _equal_phones(truth: Any, pred: Any) -> bool:
    t_norm = normalize_phone(truth)
    p_norm = normalize_phone(pred)
    if not t_norm and not p_norm:
        return True
    if t_norm.startswith("+") and p_norm.startswith("+"):
        return t_norm == p_norm
    return _digits_only(t_norm) == _digits_only(p_norm)


def _equal_dates(truth: Any, pred: Any) -> bool:
    return normalize_date(truth) == normalize_date(pred)


def score_contact(truth_payload: dict[str, Any], pred_payload: dict[str, Any]) -> float:
    fields = ["full_name", "email", "phone", "linkedin_url", "location"]
    comparators = {
        "full_name": _equal_strings,
        "email": _equal_emails,
        "phone": _equal_phones,
        "linkedin_url": _equal_strings,
        "location": _equal_strings,
    }

    matches = 0
    for field in fields:
        truth_value = _get_contact_value(truth_payload, field)
        pred_value = _get_contact_value(pred_payload, field)
        if comparators[field](truth_value, pred_value):
            matches += 1

    return matches / len(fields)


def _extract_work_history(payload: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = [
        payload.get("work_history"),
        payload.get("work_experience"),
        payload.get("experience"),
    ]

    structured = payload.get("structured_resume")
    if isinstance(structured, dict):
        candidates.insert(0, structured.get("work_experience"))

    for value in candidates:
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]

    return []


def _get_job_field(job: dict[str, Any], field_name: str) -> Any:
    if field_name == "company_name":
        return job.get("company_name") or job.get("company")
    if field_name == "client_name":
        return job.get("client_name") or job.get("client")
    if field_name == "job_title":
        return job.get("job_title") or job.get("title")
    if field_name == "start_date":
        return job.get("start_date")
    if field_name == "end_date":
        return job.get("end_date")
    raise ValueError(f"Unsupported job field: {field_name}")


def _job_match_score(truth_job: dict[str, Any], pred_job: dict[str, Any]) -> float:
    fields = ["company_name", "client_name", "job_title", "start_date", "end_date"]

    matches = 0
    for field in fields:
        truth_value = _get_job_field(truth_job, field)
        pred_value = _get_job_field(pred_job, field)

        if field in {"start_date", "end_date"}:
            ok = _equal_dates(truth_value, pred_value)
        else:
            ok = _equal_strings(truth_value, pred_value)

        matches += int(ok)

    return matches / len(fields)


def score_work_history(truth_payload: dict[str, Any], pred_payload: dict[str, Any]) -> float:
    truth_jobs = _extract_work_history(truth_payload)
    pred_jobs = _extract_work_history(pred_payload)

    if not truth_jobs:
        return 1.0 if not pred_jobs else 0.0

    remaining = pred_jobs[:]
    per_truth_scores: list[float] = []

    for truth_job in truth_jobs:
        if not remaining:
            per_truth_scores.append(0.0)
            continue

        best_idx = 0
        best_score = -1.0
        for idx, pred_job in enumerate(remaining):
            score = _job_match_score(truth_job, pred_job)
            if score > best_score:
                best_score = score
                best_idx = idx

        per_truth_scores.append(max(best_score, 0.0))
        remaining.pop(best_idx)

    return sum(per_truth_scores) / len(per_truth_scores)


def score_skills_f1(truth_payload: dict[str, Any], pred_payload: dict[str, Any]) -> SkillsF1:
    truth_skills_raw = truth_payload.get("skills")
    pred_skills_raw = pred_payload.get("skills")

    structured_truth = truth_payload.get("structured_resume")
    if isinstance(structured_truth, dict) and isinstance(structured_truth.get("skills"), list):
        truth_skills_raw = structured_truth.get("skills")

    structured_pred = pred_payload.get("structured_resume")
    if isinstance(structured_pred, dict) and isinstance(structured_pred.get("skills"), list):
        pred_skills_raw = structured_pred.get("skills")

    truth_skills = (
        {normalize_skill(item) for item in truth_skills_raw}
        if isinstance(truth_skills_raw, list)
        else set()
    )
    pred_skills = (
        {normalize_skill(item) for item in pred_skills_raw}
        if isinstance(pred_skills_raw, list)
        else set()
    )

    truth_skills.discard("")
    pred_skills.discard("")

    tp = len(truth_skills & pred_skills)
    fp = len(pred_skills - truth_skills)
    fn = len(truth_skills - pred_skills)

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0

    return SkillsF1(precision=precision, recall=recall, f1=f1)


def score_resume(truth_payload: dict[str, Any], pred_payload: dict[str, Any]) -> ResumeScore:
    contact_accuracy = score_contact(truth_payload, pred_payload)
    work_accuracy = score_work_history(truth_payload, pred_payload)
    skills_f1 = score_skills_f1(truth_payload, pred_payload)

    overall = (
        _CONTACT_WEIGHT * contact_accuracy
        + _WORK_WEIGHT * work_accuracy
        + _SKILLS_WEIGHT * skills_f1.f1
    )

    return ResumeScore(
        contact_accuracy=contact_accuracy,
        work_accuracy=work_accuracy,
        skills_f1=skills_f1,
        overall=overall,
    )


def score_dataset(pairs: Iterable[tuple[dict[str, Any], dict[str, Any]]]) -> DatasetScore:
    contact_scores: list[float] = []
    work_scores: list[float] = []
    skill_precisions: list[float] = []
    skill_recalls: list[float] = []
    skill_f1s: list[float] = []
    overall_scores: list[float] = []

    for truth_payload, pred_payload in pairs:
        score = score_resume(truth_payload, pred_payload)
        contact_scores.append(score.contact_accuracy)
        work_scores.append(score.work_accuracy)
        skill_precisions.append(score.skills_f1.precision)
        skill_recalls.append(score.skills_f1.recall)
        skill_f1s.append(score.skills_f1.f1)
        overall_scores.append(score.overall)

    n = len(overall_scores)
    if n == 0:
        return DatasetScore(
            contact_accuracy=0.0,
            work_accuracy=0.0,
            skills_f1=SkillsF1(precision=0.0, recall=0.0, f1=0.0),
            overall=0.0,
        )

    return DatasetScore(
        contact_accuracy=sum(contact_scores) / n,
        work_accuracy=sum(work_scores) / n,
        skills_f1=SkillsF1(
            precision=sum(skill_precisions) / n,
            recall=sum(skill_recalls) / n,
            f1=sum(skill_f1s) / n,
        ),
        overall=sum(overall_scores) / n,
    )


def print_dataset_score(score: DatasetScore) -> None:
    print(f"contact accuracy: {score.contact_accuracy:.3f}")
    print(f"work accuracy: {score.work_accuracy:.3f}")
    print(f"skills F1: {score.skills_f1.f1:.3f}")
    print(f"overall weighted score: {score.overall:.3f}")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def iter_fixture_pairs(fixtures_dir: Path, pred_filename: str = "pred.json"):
    for case_dir in sorted(fixtures_dir.iterdir()):
        if not case_dir.is_dir():
            continue
        if not case_dir.name.startswith("sample_"):
            continue
        truth_path = case_dir / "truth.json"
        pred_path = case_dir / pred_filename
        if truth_path.exists() and pred_path.exists():
            yield load_json(truth_path), load_json(pred_path)


def main() -> None:
    fixtures_dir = Path(__file__).resolve().parents[1] / "fixtures" / "resumes"
    score = score_dataset(iter_fixture_pairs(fixtures_dir))
    print_dataset_score(score)


if __name__ == "__main__":
    main()
