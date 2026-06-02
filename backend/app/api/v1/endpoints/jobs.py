from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
import structlog
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import enforce_rate_limit, get_current_user, get_db
from app.models.parsing_job import ParsingJob
from app.models.job_description import JobDescription
from app.schemas.job import JobCreate, JobUpdate, JobResponse

router = APIRouter()

@router.get("/jobs", response_model=dict)
def get_jobs(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    enforce_rate_limit(current_user.email, limit=100, per_seconds=60)
    jobs = db.execute(select(JobDescription)).scalars().all()
    # Manual serialization since frontend expects { "jobs": [...] }
    return {"jobs": [
        {
            "id": str(j.id),
            "title": j.title,
            "department": j.department,
            "location": j.location,
            "employment_type": j.employment_type,
            "status": j.status,
            "created_at": j.created_at.isoformat() if j.created_at else None,
            "updated_at": j.updated_at.isoformat() if j.updated_at else None,
        } for j in jobs
    ]}

@router.post("/jobs", response_model=dict)
def create_job(
    job_in: JobCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_job = JobDescription(
        title=job_in.title,
        description=job_in.description,
        department=job_in.department,
        min_experience_years=job_in.min_experience_years,
        max_experience_years=job_in.max_experience_years,
        education_requirement=job_in.education_requirement,
        employment_type=job_in.employment_type,
        seniority_level=job_in.seniority_level,
        location=job_in.location,
        salary_range=job_in.salary_range,
        status=job_in.status or "active",
        required_skills=job_in.required_skills or [],
        preferred_skills=job_in.preferred_skills or []
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    return {"job": {
        "id": str(db_job.id),
        "title": db_job.title,
        "description": db_job.description,
        "department": db_job.department,
        "min_experience_years": db_job.min_experience_years,
        "max_experience_years": db_job.max_experience_years,
        "education_requirement": db_job.education_requirement,
        "employment_type": db_job.employment_type,
        "seniority_level": db_job.seniority_level,
        "location": db_job.location,
        "salary_range": db_job.salary_range,
        "status": db_job.status,
        "required_skills": db_job.required_skills,
        "preferred_skills": db_job.preferred_skills,
        "created_at": db_job.created_at.isoformat() if db_job.created_at else None,
        "updated_at": db_job.updated_at.isoformat() if db_job.updated_at else None,
    }}

@router.get("/jobs/{job_id}", response_model=dict)
def get_job(
    job_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.execute(select(JobDescription).where(JobDescription.id == job_id)).scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"job": {
        "id": str(job.id),
        "title": job.title,
        "description": job.description,
        "department": job.department,
        "min_experience_years": job.min_experience_years,
        "max_experience_years": job.max_experience_years,
        "education_requirement": job.education_requirement,
        "employment_type": job.employment_type,
        "seniority_level": job.seniority_level,
        "location": job.location,
        "salary_range": job.salary_range,
        "status": job.status,
        "required_skills": job.required_skills,
        "preferred_skills": job.preferred_skills,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "updated_at": job.updated_at.isoformat() if job.updated_at else None,
    }}

@router.put("/jobs/{job_id}", response_model=dict)
def update_job(
    job_id: UUID,
    job_in: JobUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.execute(select(JobDescription).where(JobDescription.id == job_id)).scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    update_data = job_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)
        
    db.commit()
    db.refresh(job)
    
    return {"job": {
        "id": str(job.id),
        "title": job.title,
        "description": job.description,
        "department": job.department,
        "min_experience_years": job.min_experience_years,
        "max_experience_years": job.max_experience_years,
        "education_requirement": job.education_requirement,
        "employment_type": job.employment_type,
        "seniority_level": job.seniority_level,
        "location": job.location,
        "salary_range": job.salary_range,
        "status": job.status,
        "required_skills": job.required_skills,
        "preferred_skills": job.preferred_skills,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "updated_at": job.updated_at.isoformat() if job.updated_at else None,
    }}

@router.delete("/jobs/{job_id}")
def delete_job(
    job_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.execute(select(JobDescription).where(JobDescription.id == job_id)).scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    db.delete(job)
    db.commit()
    return {"success": True, "message": "Job deleted successfully"}

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
