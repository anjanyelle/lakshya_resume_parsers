from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
import structlog
from sqlalchemy.orm import Session

from app.api.deps import enforce_rate_limit, require_role, get_db
from app.models import Candidate
from app.schemas.candidate import CandidateRead
from app.utils.audit import log_audit

router = APIRouter()


@router.get("/gdpr/export/{candidate_id}")
def gdpr_export(
    candidate_id: UUID,
    current_user=Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> dict:
    structlog.contextvars.bind_contextvars(candidate_id=str(candidate_id))
    enforce_rate_limit(current_user.email, limit=10, per_seconds=60)
    candidate = (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id, Candidate.tenant_id == current_user.tenant_id)
        .first()
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    payload = CandidateRead.model_validate(candidate).model_dump()
    log_audit(
        db,
        user_id=str(current_user.id),
        action="gdpr_export",
        resource_type="candidate",
        resource_id=str(candidate_id),
        ip_address=None,
    )
    return payload


@router.delete("/gdpr/delete/{candidate_id}")
def gdpr_delete(
    candidate_id: UUID,
    current_user=Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    structlog.contextvars.bind_contextvars(candidate_id=str(candidate_id))
    enforce_rate_limit(current_user.email, limit=5, per_seconds=60)
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
        action="gdpr_delete",
        resource_type="candidate",
        resource_id=str(candidate_id),
        ip_address=None,
    )
    return {"status": "deleted"}
