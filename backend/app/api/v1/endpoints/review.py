from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import enforce_rate_limit, get_current_user, get_db, require_role
from app.core.config import get_settings
from app.models import Candidate, ReviewStatus
from app.schemas.candidate import CandidateRead
from app.schemas.review import CorrectionAnalytics, ReviewQueueItem
from app.utils.review import correction_analytics

router = APIRouter()


@router.get("/review-queue", response_model=list[ReviewQueueItem])
def review_queue(
    status: ReviewStatus | None = Query(default=None),
    assigned_to: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    current_user=Depends(require_role("admin", "recruiter")),
    db: Session = Depends(get_db),
) -> list[ReviewQueueItem]:
    enforce_rate_limit(current_user.email, limit=60, per_seconds=60)
    settings = get_settings()
    query = db.query(Candidate).filter(
        Candidate.tenant_id == current_user.tenant_id,
        Candidate.review_confidence.isnot(None),
        Candidate.review_confidence < settings.REVIEW_CONFIDENCE_THRESHOLD,
    )
    if status:
        query = query.filter(Candidate.review_status == status)
    if assigned_to:
        query = query.filter(Candidate.review_assigned_to == assigned_to)
    candidates = query.offset(skip).limit(limit).all()
    return [
        ReviewQueueItem(
            candidate=CandidateRead.model_validate(candidate),
            confidence=candidate.review_confidence,
            review_status=candidate.review_status,
            review_assigned_to=candidate.review_assigned_to,
        )
        for candidate in candidates
    ]


@router.get("/corrections/analytics", response_model=CorrectionAnalytics)
def corrections_analytics(
    current_user=Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> CorrectionAnalytics:
    enforce_rate_limit(current_user.email, limit=30, per_seconds=60)
    return CorrectionAnalytics(**correction_analytics(db))
