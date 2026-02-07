from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
import structlog
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import enforce_rate_limit, get_current_user, get_db
from app.models.parsing_job import ParsingJob

router = APIRouter()


@router.get("/jobs/{job_id}/status")
def job_status(
    job_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str | None]:
    structlog.contextvars.bind_contextvars(job_id=job_id)
    try:
        import sentry_sdk

        sentry_sdk.set_tag("job_id", job_id)
    except Exception:
        pass
    enforce_rate_limit(current_user.email, limit=60, per_seconds=60)
    job = db.execute(select(ParsingJob).where(ParsingJob.id == job_id)).scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": str(job.id),
        "status": job.status.value,
        "last_stage": job.last_stage,
        "error_message": job.error_message,
    }


@router.get("/jobs/{job_id}/logs")
def job_logs(
    job_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str | None]:
    structlog.contextvars.bind_contextvars(job_id=job_id)
    try:
        import sentry_sdk

        sentry_sdk.set_tag("job_id", job_id)
    except Exception:
        pass
    enforce_rate_limit(current_user.email, limit=30, per_seconds=60)
    job = db.execute(select(ParsingJob).where(ParsingJob.id == job_id)).scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": str(job.id),
        "last_stage": job.last_stage,
        "error_message": job.error_message,
    }
