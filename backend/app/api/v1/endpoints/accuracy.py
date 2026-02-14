from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.api.deps import enforce_rate_limit, get_current_user, get_db
from app.models import Correction, CorrectionStat, ParsingJob
from app.models.parsing_job import ParsingJobStatus

router = APIRouter()


@router.get("/accuracy/overview")
def accuracy_overview(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, object]:
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
    avg_conf = db.query(func.avg(ParsingJob.confidence_score)).scalar() or 0.0
    corrections = db.query(func.count(Correction.id)).scalar() or 0
    correction_rate = (corrections / total) * 100 if total else 0.0

    avg_time = (
        db.query(func.avg(ParsingJob.completed_at - ParsingJob.started_at))
        .filter(ParsingJob.completed_at.isnot(None))
        .scalar()
    )
    avg_seconds = avg_time.total_seconds() if isinstance(avg_time, timedelta) else 0.0

    top_fields = (
        db.query(CorrectionStat.field_name, CorrectionStat.correction_count)
        .order_by(CorrectionStat.correction_count.desc())
        .limit(5)
        .all()
    )
    field_scores = []
    for field, count in top_fields:
        score = 1.0 if total == 0 else max(0.4, 1 - (count / max(total, 1)))
        field_scores.append({"label": field, "score": round(score, 2)})

    recent_jobs = (
        db.query(ParsingJob)
        .order_by(desc(ParsingJob.started_at))
        .limit(5)
        .all()
    )
    recent_runs = [
        {
            "job_id": str(job.id),
            "status": job.status.value,
            "confidence": round(job.confidence_score or 0.0, 2),
            "notes": job.last_stage or "n/a",
        }
        for job in recent_jobs
    ]

    return {
        "total_jobs": total,
        "success_jobs": success,
        "failed_jobs": failed,
        "success_rate": round((success / total) * 100, 2) if total else 0.0,
        "avg_processing_seconds": round(avg_seconds, 2),
        "avg_confidence": round(avg_conf, 2),
        "correction_rate": round(correction_rate, 2),
        "section_scores": field_scores,
        "recent_runs": recent_runs,
    }
