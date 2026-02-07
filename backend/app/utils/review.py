from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import (
    Candidate,
    Correction,
    CorrectionPattern,
    CorrectionStat,
    ParsingJob,
    Skill,
    SkillSuggestion,
    WorkHistory,
)


def get_latest_job(db: Session, candidate_id) -> ParsingJob | None:
    return (
        db.execute(
            select(ParsingJob)
            .where(ParsingJob.candidate_id == candidate_id)
            .order_by(ParsingJob.started_at.desc())
        )
        .scalars()
        .first()
    )


def compute_field_confidences(parsed_data: dict | None) -> dict[str, float]:
    if not parsed_data:
        return {}
    confidences: dict[str, float] = {}

    contact = parsed_data.get("contact", {})
    if contact:
        if contact.get("name"):
            confidences["name"] = float(contact["name"].get("confidence", 0.0))
        if contact.get("location"):
            confidences["location"] = float(contact["location"].get("confidence", 0.0))
        email_conf = _min_confidence(contact.get("emails", []))
        if email_conf is not None:
            confidences["email"] = email_conf
        phone_conf = _min_confidence(contact.get("phones", []))
        if phone_conf is not None:
            confidences["phone"] = phone_conf

    for field in ("work_experience", "education", "certifications"):
        conf = _min_confidence(parsed_data.get(field, []))
        if conf is not None:
            confidences[field] = conf

    skills_conf = _min_confidence(parsed_data.get("skills", []))
    if skills_conf is not None:
        confidences["skills"] = skills_conf

    return confidences


def compute_review_flags(
    parsed_data: dict | None,
    overall_confidence: float | None,
    field_threshold: float,
    discrepancies: list[str] | None = None,
) -> dict[str, Any]:
    field_confidences = compute_field_confidences(parsed_data)
    flagged_fields = {
        field: confidence
        for field, confidence in field_confidences.items()
        if confidence < field_threshold
    }
    return {
        "overall_confidence": overall_confidence,
        "flagged_fields": flagged_fields,
        "discrepancies": discrepancies or [],
    }


def find_date_overlaps(db: Session, candidate_id) -> list[str]:
    jobs = (
        db.query(WorkHistory)
        .filter(WorkHistory.candidate_id == candidate_id)
        .order_by(WorkHistory.start_date.asc())
        .all()
    )
    overlaps: list[str] = []
    for idx in range(len(jobs) - 1):
        current = jobs[idx]
        nxt = jobs[idx + 1]
        if not current.end_date or not nxt.start_date:
            continue
        if nxt.start_date <= current.end_date:
            overlaps.append(
                f"Overlap between {current.company_name} and {nxt.company_name}"
            )
    return overlaps


def apply_correction_patterns(db: Session, candidate: Candidate) -> list[str]:
    settings = get_settings()
    applied: list[str] = []
    patterns = (
        db.query(CorrectionPattern)
        .filter(CorrectionPattern.count >= settings.CORRECTION_PATTERN_MIN_COUNT)
        .all()
    )
    for pattern in patterns:
        field = pattern.field_name
        if not hasattr(candidate, field):
            continue
        current = getattr(candidate, field)
        if current is None:
            continue
        if str(current) == pattern.original_value:
            setattr(candidate, field, pattern.corrected_value)
            applied.append(field)
    return applied


def suggest_corrections(db: Session, candidate: Candidate) -> dict[str, str]:
    settings = get_settings()
    suggestions: dict[str, str] = {}
    patterns = (
        db.query(CorrectionPattern)
        .filter(CorrectionPattern.count >= settings.CORRECTION_PATTERN_MIN_COUNT)
        .all()
    )
    for pattern in patterns:
        field = pattern.field_name
        if not hasattr(candidate, field):
            continue
        current = getattr(candidate, field)
        if current is None:
            continue
        if str(current) == pattern.original_value:
            suggestions[field] = pattern.corrected_value
    return suggestions


def record_correction(
    db: Session,
    *,
    candidate_id,
    field_name: str,
    original_value: str | None,
    corrected_value: str | None,
    corrected_by: str | None,
) -> Correction:
    correction = Correction(
        candidate_id=candidate_id,
        field_name=field_name,
        original_value=original_value,
        corrected_value=corrected_value,
        corrected_by=corrected_by,
    )
    db.add(correction)

    stat = db.get(CorrectionStat, field_name)
    if not stat:
        stat = CorrectionStat(field_name=field_name, correction_count=1)
        db.add(stat)
    else:
        stat.correction_count += 1

    if original_value is not None and corrected_value is not None:
        pattern = (
            db.query(CorrectionPattern)
            .filter(
                CorrectionPattern.field_name == field_name,
                CorrectionPattern.original_value == original_value,
                CorrectionPattern.corrected_value == corrected_value,
            )
            .first()
        )
        if pattern:
            pattern.count += 1
            pattern.last_seen_at = datetime.now(timezone.utc)
        else:
            db.add(
                CorrectionPattern(
                    field_name=field_name,
                    original_value=original_value,
                    corrected_value=corrected_value,
                )
            )

    return correction


def suggest_skills(db: Session, corrected_value: str, source: str | None = None) -> None:
    skills = {item.strip() for item in corrected_value.split(",") if item.strip()}
    if not skills:
        return
    existing = {row[0] for row in db.query(Skill.normalized_name).all()}
    for skill in skills:
        normalized = skill.lower()
        if normalized in existing:
            continue
        db.add(
            SkillSuggestion(
                skill_name=skill,
                normalized_name=normalized,
                source=source,
                notes="Suggested from correction",
            )
        )


def correction_analytics(db: Session) -> dict[str, Any]:
    fields = (
        db.query(CorrectionStat.field_name, CorrectionStat.correction_count)
        .order_by(CorrectionStat.correction_count.desc())
        .limit(10)
        .all()
    )
    most_corrected = [
        {"field_name": name, "count": count} for name, count in fields
    ]

    daily = (
        db.query(func.date(Correction.corrected_at), func.count())
        .group_by(func.date(Correction.corrected_at))
        .order_by(func.date(Correction.corrected_at))
        .all()
    )
    corrections_over_time = [
        {"date": str(day), "count": count} for day, count in daily
    ]

    reviewers = (
        db.query(Correction.corrected_by, func.count())
        .group_by(Correction.corrected_by)
        .order_by(func.count().desc())
        .all()
    )
    reviewer_performance = [
        {"reviewer": reviewer or "unknown", "corrections": count}
        for reviewer, count in reviewers
    ]

    return {
        "most_corrected_fields": most_corrected,
        "corrections_over_time": corrections_over_time,
        "reviewer_performance": reviewer_performance,
    }


def _min_confidence(items: list[dict]) -> float | None:
    if not items:
        return None
    confidences = [float(item.get("confidence", 0.0)) for item in items]
    return min(confidences) if confidences else None
