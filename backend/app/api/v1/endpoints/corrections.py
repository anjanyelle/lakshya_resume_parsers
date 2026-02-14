from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.api.deps import enforce_rate_limit, get_current_user, get_db
from app.models import Candidate, Correction

router = APIRouter()


@router.get("/corrections/recent")
def recent_corrections(
    limit: int = Query(default=50, ge=1, le=200),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict[str, str | None]]:
    enforce_rate_limit(current_user.email, limit=60, per_seconds=60)
    rows = (
        db.execute(
            select(
                Correction,
                Candidate.full_name,
                Candidate.email,
            )
            .join(Candidate, Candidate.id == Correction.candidate_id)
            .where(Candidate.tenant_id == current_user.tenant_id)
            .order_by(desc(Correction.corrected_at))
            .limit(limit)
        )
        .all()
    )
    results: list[dict[str, str | None]] = []
    for correction, full_name, email in rows:
        results.append(
            {
                "candidate_name": full_name,
                "candidate_email": email,
                "field": correction.field_name,
                "original": correction.original_value,
                "corrected": correction.corrected_value,
                "reviewer": correction.corrected_by,
                "corrected_at": correction.corrected_at.isoformat(),
            }
        )
    return results
