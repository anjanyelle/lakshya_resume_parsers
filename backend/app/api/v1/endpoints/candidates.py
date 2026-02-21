from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
import dateparser
import structlog
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.deps import enforce_rate_limit, get_current_user, get_db, require_role
from app.core.config import get_settings
from app.models import Candidate, Certification, ParsingJob, ReviewStatus, WorkHistory
from app.schemas.candidate import CandidateRead, CandidateUpdate, ParsingJobRead
from app.schemas.public import CandidatePublicRead
from app.schemas.review import CandidateReviewResponse, CorrectionRequest
from app.services.storage import generate_presigned_url
from app.utils.audit import log_audit
from app.utils.pii import hash_value
from app.utils.review import (
    compute_review_flags,
    find_date_overlaps,
    get_latest_job,
    record_correction,
    suggest_corrections,
    suggest_skills,
)
from app.workers.pipeline import start_parsing_workflow

router = APIRouter()
logger = logging.getLogger(__name__)


def _parse_optional_date(value: str | None):
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw).date()
    except ValueError:
        parsed = dateparser.parse(raw, settings={"PREFER_DAY_OF_MONTH": "first"})
        return parsed.date() if parsed else None


def _parse_optional_bool(value: str | None):
    raw = str(value or "").strip().lower()
    if raw in {"true", "1", "yes", "y"}:
        return True
    if raw in {"false", "0", "no", "n"}:
        return False
    return None


@router.get("/candidates", response_model=list[CandidatePublicRead])
def list_candidates(
    q: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CandidatePublicRead]:
    enforce_rate_limit(current_user.email, limit=60, per_seconds=60)
    query = db.query(Candidate).filter(Candidate.tenant_id == current_user.tenant_id)
    if status:
        query = query.filter(Candidate.status == status)
    if q:
        like = f"%{q}%"
        filters = [
            Candidate.full_name.ilike(like),
            Candidate.current_company.ilike(like),
            Candidate.current_title.ilike(like),
            Candidate.location.ilike(like),
        ]
        if "@" in q:
            filters.append(Candidate.email_hash == hash_value(q))
        query = query.filter(or_(*filters))
    candidates = query.offset(skip).limit(limit).all()
    return [CandidatePublicRead.model_validate(c) for c in candidates]


@router.get("/candidates/{candidate_id}", response_model=CandidatePublicRead)
def get_candidate(
    candidate_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CandidatePublicRead:
    structlog.contextvars.bind_contextvars(candidate_id=str(candidate_id))
    enforce_rate_limit(current_user.email, limit=60, per_seconds=60)
    candidate = (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id, Candidate.tenant_id == current_user.tenant_id)
        .first()
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return CandidatePublicRead.model_validate(candidate)


@router.put("/candidates/{candidate_id}", response_model=CandidatePublicRead)
def update_candidate(
    candidate_id: UUID,
    payload: CandidateUpdate,
    current_user=Depends(require_role("admin", "recruiter")),
    db: Session = Depends(get_db),
) -> CandidatePublicRead:
    structlog.contextvars.bind_contextvars(candidate_id=str(candidate_id))
    enforce_rate_limit(current_user.email, limit=30, per_seconds=60)
    candidate = (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id, Candidate.tenant_id == current_user.tenant_id)
        .first()
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(candidate, field, value)
    if payload.email:
        candidate.email_hash = hash_value(payload.email)
    if payload.consent_given and not payload.consent_date:
        from datetime import datetime

        candidate.consent_date = datetime.utcnow()
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    log_audit(
        db,
        user_id=str(current_user.id),
        action="update",
        resource_type="candidate",
        resource_id=str(candidate.id),
        ip_address=None,
    )
    return CandidatePublicRead.model_validate(candidate)


@router.delete("/candidates/{candidate_id}")
def delete_candidate(
    candidate_id: UUID,
    current_user=Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    structlog.contextvars.bind_contextvars(candidate_id=str(candidate_id))
    enforce_rate_limit(current_user.email, limit=20, per_seconds=60)
    candidate = (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id, Candidate.tenant_id == current_user.tenant_id)
        .first()
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    db.delete(candidate)
    db.commit()
    log_audit(
        db,
        user_id=str(current_user.id),
        action="delete",
        resource_type="candidate",
        resource_id=str(candidate.id),
        ip_address=None,
    )
    return {"status": "deleted"}


@router.get("/candidates/{candidate_id}/resume")
def download_resume(
    candidate_id: UUID,
    request: Request,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    structlog.contextvars.bind_contextvars(candidate_id=str(candidate_id))
    enforce_rate_limit(current_user.email, limit=30, per_seconds=60)
    job = (
        db.execute(
            select(ParsingJob)
            .join(Candidate, Candidate.id == ParsingJob.candidate_id)
            .where(
                ParsingJob.candidate_id == candidate_id,
                Candidate.tenant_id == current_user.tenant_id,
            )
            .order_by(ParsingJob.started_at.desc())
        )
        .scalars()
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Resume not found")
    if job.file_path.startswith("s3://"):
        url = generate_presigned_url(job.file_path)
    else:
        base_url = str(request.base_url).rstrip("/")
        url = f"{base_url}{get_settings().API_V1_STR}/files/{job.id}"
    log_audit(
        db,
        user_id=str(current_user.id),
        action="download_resume",
        resource_type="candidate",
        resource_id=str(candidate_id),
        ip_address=None,
    )
    return {"download_url": url}


@router.post("/candidates/{candidate_id}/reprocess")
def reprocess_candidate(
    candidate_id: UUID,
    current_user=Depends(require_role("admin", "recruiter")),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    structlog.contextvars.bind_contextvars(candidate_id=str(candidate_id))
    enforce_rate_limit(current_user.email, limit=10, per_seconds=60)
    job = (
        db.execute(
            select(ParsingJob)
            .join(Candidate, Candidate.id == ParsingJob.candidate_id)
            .where(
                ParsingJob.candidate_id == candidate_id,
                Candidate.tenant_id == current_user.tenant_id,
            )
            .order_by(ParsingJob.started_at.desc())
        )
        .scalars()
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Parsing job not found")

    new_job = ParsingJob(
        candidate_id=job.candidate_id,
        filename=job.filename,
        file_path=job.file_path,
    )
    db.add(new_job)
    db.commit()
    job_id = str(new_job.id)

    start_parsing_workflow(job_id)
    refreshed = db.execute(select(ParsingJob).where(ParsingJob.id == new_job.id)).scalar_one_or_none()
    log_audit(
        db,
        user_id=str(current_user.id),
        action="reprocess",
        resource_type="candidate",
        resource_id=str(candidate_id),
        ip_address=None,
    )
    status = refreshed.status.value if refreshed else "processing"
    return {"job_id": job_id, "status": status}


@router.get("/candidates/{candidate_id}/review", response_model=CandidateReviewResponse)
def get_candidate_review(
    candidate_id: UUID,
    current_user=Depends(require_role("admin", "recruiter")),
    db: Session = Depends(get_db),
) -> CandidateReviewResponse:
    structlog.contextvars.bind_contextvars(candidate_id=str(candidate_id))
    enforce_rate_limit(current_user.email, limit=30, per_seconds=60)
    candidate = (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id, Candidate.tenant_id == current_user.tenant_id)
        .first()
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    job = get_latest_job(db, candidate_id)
    parsed_data = job.parsed_data if job else None
    discrepancies = find_date_overlaps(db, candidate_id)
    review_flags = compute_review_flags(
        parsed_data,
        job.confidence_score if job else None,
        get_settings().REVIEW_FIELD_THRESHOLD,
        discrepancies,
    )
    suggestions = suggest_corrections(db, candidate)

    return CandidateReviewResponse(
        candidate=CandidateRead.model_validate(candidate),
        latest_job=ParsingJobRead.model_validate(job) if job else None,
        review_flags=review_flags,
        suggested_corrections=suggestions or None,
    )


@router.put("/candidates/{candidate_id}/corrections", response_model=CandidatePublicRead)
def submit_corrections(
    candidate_id: UUID,
    payload: CorrectionRequest,
    current_user=Depends(require_role("admin", "recruiter")),
    db: Session = Depends(get_db),
) -> CandidatePublicRead:
    structlog.contextvars.bind_contextvars(candidate_id=str(candidate_id))
    enforce_rate_limit(current_user.email, limit=30, per_seconds=60)
    candidate = (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id, Candidate.tenant_id == current_user.tenant_id)
        .first()
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    for correction in payload.corrections:
        field = correction.field_name
        corrected_value = correction.corrected_value

        if field.startswith("work_history."):
            parts = field.split(".")
            if len(parts) != 3:
                raise HTTPException(status_code=400, detail=f"Invalid correction field: {field}")
            _, row_id, attr = parts
            try:
                row_uuid = UUID(row_id)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=f"Invalid work history id: {row_id}") from exc

            row = (
                db.query(WorkHistory)
                .filter(WorkHistory.id == row_uuid, WorkHistory.candidate_id == candidate.id)
                .first()
            )
            if not row:
                raise HTTPException(status_code=404, detail="Work history item not found")

            allowed = {
                "company_name",
                "client_name",
                "job_title",
                "start_date",
                "end_date",
                "is_current",
                "location",
                "description",
            }
            if attr not in allowed:
                raise HTTPException(status_code=400, detail=f"Unsupported work history field: {attr}")

            current_value = getattr(row, attr)
            if isinstance(current_value, datetime):
                original_value = current_value.isoformat()
            else:
                original_value = str(current_value) if current_value is not None else None

            parsed_value = corrected_value
            if attr in {"start_date", "end_date"}:
                parsed_value = _parse_optional_date(corrected_value)
            elif attr == "is_current":
                bool_val = _parse_optional_bool(corrected_value)
                parsed_value = bool_val if bool_val is not None else row.is_current
            else:
                parsed_value = str(corrected_value).strip() if corrected_value is not None else None
                if parsed_value == "":
                    parsed_value = None

            record_correction(
                db,
                candidate_id=candidate.id,
                field_name=field,
                original_value=original_value,
                corrected_value=str(corrected_value) if corrected_value is not None else None,
                corrected_by=str(current_user.id),
            )
            setattr(row, attr, parsed_value)
            db.add(row)
            continue

        if field.startswith("certifications."):
            parts = field.split(".")
            if len(parts) != 3:
                raise HTTPException(status_code=400, detail=f"Invalid correction field: {field}")
            _, row_id, attr = parts
            try:
                row_uuid = UUID(row_id)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=f"Invalid certification id: {row_id}") from exc

            row = (
                db.query(Certification)
                .filter(Certification.id == row_uuid, Certification.candidate_id == candidate.id)
                .first()
            )
            if not row:
                raise HTTPException(status_code=404, detail="Certification item not found")

            allowed = {
                "name",
                "issuing_organization",
                "issue_date",
                "expiry_date",
                "credential_id",
            }
            if attr not in allowed:
                raise HTTPException(status_code=400, detail=f"Unsupported certification field: {attr}")

            current_value = getattr(row, attr)
            original_value = str(current_value) if current_value is not None else None

            parsed_value = corrected_value
            if attr in {"issue_date", "expiry_date"}:
                parsed_value = _parse_optional_date(corrected_value)
            else:
                parsed_value = str(corrected_value).strip() if corrected_value is not None else None
                if parsed_value == "":
                    parsed_value = None

            record_correction(
                db,
                candidate_id=candidate.id,
                field_name=field,
                original_value=original_value,
                corrected_value=str(corrected_value) if corrected_value is not None else None,
                corrected_by=str(current_user.id),
            )
            if attr == "name" and parsed_value is None:
                raise HTTPException(status_code=400, detail="Certification name is required")
            setattr(row, attr, parsed_value)
            db.add(row)
            continue

        if hasattr(candidate, field):
            current_value = getattr(candidate, field)
            original_value = str(current_value) if current_value is not None else None
        else:
            original_value = correction.original_value

        record_correction(
            db,
            candidate_id=candidate.id,
            field_name=field,
            original_value=original_value,
            corrected_value=corrected_value,
            corrected_by=str(current_user.id),
        )
        if hasattr(candidate, field) and corrected_value is not None:
            setattr(candidate, field, corrected_value)
            if field == "email":
                candidate.email_hash = hash_value(corrected_value)
        if field == "skills" and corrected_value:
            suggest_skills(db, corrected_value, source="manual_correction")

    if payload.corrections and candidate.review_status == ReviewStatus.PENDING:
        candidate.review_status = ReviewStatus.IN_REVIEW
    if payload.review_notes is not None:
        candidate.review_notes = payload.review_notes
    if payload.review_status is not None:
        candidate.review_status = payload.review_status
        if payload.review_status == ReviewStatus.REJECTED:
            candidate.review_rejected_at = datetime.utcnow()
            candidate.review_rejected_by = str(current_user.id)
        if payload.review_status == ReviewStatus.APPROVED:
            candidate.review_approved_at = datetime.utcnow()
            candidate.review_approved_by = str(current_user.id)
    if payload.review_assigned_to is not None:
        candidate.review_assigned_to = payload.review_assigned_to
        if candidate.review_status == ReviewStatus.PENDING:
            candidate.review_status = ReviewStatus.IN_REVIEW

    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    log_audit(
        db,
        user_id=str(current_user.id),
        action="corrections_submitted",
        resource_type="candidate",
        resource_id=str(candidate.id),
        ip_address=None,
        details={"corrections": [c.field_name for c in payload.corrections]},
    )
    return CandidatePublicRead.model_validate(candidate)


@router.post("/candidates/{candidate_id}/approve", response_model=CandidatePublicRead)
def approve_candidate(
    candidate_id: UUID,
    current_user=Depends(require_role("admin", "recruiter")),
    db: Session = Depends(get_db),
) -> CandidatePublicRead:
    structlog.contextvars.bind_contextvars(candidate_id=str(candidate_id))
    enforce_rate_limit(current_user.email, limit=20, per_seconds=60)
    candidate = (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id, Candidate.tenant_id == current_user.tenant_id)
        .first()
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    candidate.review_status = ReviewStatus.APPROVED
    candidate.review_approved_at = datetime.utcnow()
    candidate.review_approved_by = str(current_user.id)
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    log_audit(
        db,
        user_id=str(current_user.id),
        action="review_approved",
        resource_type="candidate",
        resource_id=str(candidate.id),
        ip_address=None,
    )
    return CandidatePublicRead.model_validate(candidate)
