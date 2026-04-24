from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
import structlog
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import enforce_rate_limit, get_current_user, get_db
from app.models.parsing_job import ParsingJob

router = APIRouter()


@router.get("/jobs/{job_id}/status")
def job_status(
    job_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str | None]:
    structlog.contextvars.bind_contextvars(job_id=str(job_id))
    try:
        import sentry_sdk

        sentry_sdk.set_tag("job_id", str(job_id))
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
    job_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str | None]:
    structlog.contextvars.bind_contextvars(job_id=str(job_id))
    try:
        import sentry_sdk

        sentry_sdk.set_tag("job_id", str(job_id))
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


@router.get("/jobs/{job_id}/extraction-debug")
def job_extraction_debug(
    job_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Return extraction stats for data-loss verification: raw text length,
    sample, and parsed structure counts. Use when debugging missing content.
    """
    enforce_rate_limit(current_user.email, limit=30, per_seconds=60)
    job = db.execute(select(ParsingJob).where(ParsingJob.id == job_id)).scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    raw = job.raw_text or ""
    parsed = job.parsed_data or {}
    
    # Fallback for older jobs or cases where raw_text was not saved
    if not raw and parsed:
        debug_data = parsed.get("debug", {})
        html_preview = debug_data.get("html_preview")
        if html_preview:
            # Simple tag stripping for fallback
            import re
            raw = re.sub(r'<[^>]+>', '\n', html_preview)
            raw = "\n".join([ln.strip() for ln in raw.split("\n") if ln.strip()])
    work = parsed.get("work_experience") or []
    education = parsed.get("education") or []
    certs = parsed.get("certifications") or []
    sections = parsed.get("sections") or {}
    summary_block = sections.get("summary") if isinstance(sections, dict) else {}
    summary_content = summary_block.get("content") if isinstance(summary_block, dict) else ""
    summary_len = len(str(summary_content or ""))
    work_desc_len = sum(
        len(str(e.get("description") or ""))
        for e in work
        if isinstance(e, dict)
    )
    return {
        "job_id": str(job.id),
        "stage": "extraction_debug",
        "raw_text": raw,
        "raw_text_length": len(raw),
        "raw_text_sample_first_200": raw[:200] if raw else "",
        "raw_text_sample_last_100": raw[-100:] if len(raw) > 100 else raw,
        "parsed_work_experience_count": len(work) if isinstance(work, list) else 0,
        "parsed_work_description_total_chars": work_desc_len,
        "parsed_education_count": len(education) if isinstance(education, list) else 0,
        "parsed_certifications_count": len(certs) if isinstance(certs, list) else 0,
        "parsed_summary_length": summary_len,
        "text_extraction_method": (parsed.get("text_extraction") or {}).get("method") if isinstance(parsed.get("text_extraction"), dict) else None,
        "used_ocr": (parsed.get("text_extraction") or {}).get("used_ocr") if isinstance(parsed.get("text_extraction"), dict) else None,
    }
