from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import enforce_rate_limit, get_current_user, get_db
from app.models.parsing_job import ParsingJob
from app.workers.celery_app import celery_app

router = APIRouter()


@router.get("/parsing/{job_id}")
def get_parsing_status(
    job_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str | None]:
    enforce_rate_limit(current_user.email, limit=60, per_seconds=60)
    job = db.execute(select(ParsingJob).where(ParsingJob.id == job_id)).scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Parsing job not found")

    celery_state = None
    if job.task_id:
        celery_state = celery_app.AsyncResult(job.task_id).state

    return {
        "job_id": str(job.id),
        "status": job.status.value,
        "last_stage": job.last_stage,
        "task_id": job.task_id,
        "celery_state": celery_state,
    }
