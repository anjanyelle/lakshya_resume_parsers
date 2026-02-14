from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import enforce_rate_limit, get_current_user, get_db
from app.models import CandidateSkill, ParsingJob, Skill
from app.models.parsing_job import ParsingJobStatus

router = APIRouter()


@router.get("/analytics/parsing-stats")
def parsing_stats(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, float | int]:
    enforce_rate_limit(current_user.email, limit=30, per_seconds=60)
    total = db.query(func.count(ParsingJob.id)).scalar() or 0
    success = (
        db.query(func.count(ParsingJob.id))
        .filter(ParsingJob.status == ParsingJobStatus.SUCCESS)
        .scalar()
        or 0
    )
    failed = (
        db.query(func.count(ParsingJob.id))
        .filter(ParsingJob.status == ParsingJobStatus.FAILED)
        .scalar()
        or 0
    )
    avg_time = (
        db.query(func.avg(ParsingJob.completed_at - ParsingJob.started_at))
        .filter(ParsingJob.completed_at.isnot(None))
        .scalar()
    )
    avg_seconds = avg_time.total_seconds() if isinstance(avg_time, timedelta) else 0.0
    success_rate = (success / total) * 100 if total else 0.0
    return {
        "total_jobs": total,
        "success_jobs": success,
        "failed_jobs": failed,
        "success_rate": round(success_rate, 2),
        "avg_processing_seconds": round(avg_seconds, 2),
    }


@router.get("/analytics/skill-distribution")
def skill_distribution(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict[str, int | str]]:
    enforce_rate_limit(current_user.email, limit=30, per_seconds=60)
    rows = (
        db.query(Skill.name, func.count(CandidateSkill.skill_id))
        .join(CandidateSkill, CandidateSkill.skill_id == Skill.id)
        .group_by(Skill.name)
        .order_by(func.count(CandidateSkill.skill_id).desc())
        .limit(50)
        .all()
    )
    return [{"skill": name, "count": count} for name, count in rows]
