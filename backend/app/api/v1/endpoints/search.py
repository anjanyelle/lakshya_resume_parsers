from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.api.deps import enforce_rate_limit, get_current_user, get_db
from app.models import Candidate, CandidateSkill, Education, Skill, WorkHistory
from app.schemas.candidate import CandidateRead
from app.utils.pii import hash_value

router = APIRouter()


@router.get("/search", response_model=list[CandidateRead])
def advanced_search(
    skills: Optional[list[str]] = Query(default=None),
    years_min: Optional[float] = Query(default=None),
    years_max: Optional[float] = Query(default=None),
    location: Optional[str] = Query(default=None),
    current_company: Optional[str] = Query(default=None),
    education_level: Optional[str] = Query(default=None),
    q: Optional[str] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CandidateRead]:
    enforce_rate_limit(current_user.email, limit=60, per_seconds=60)
    query = db.query(Candidate).filter(Candidate.tenant_id == current_user.tenant_id)

    if years_min is not None:
        query = query.filter(Candidate.years_experience >= years_min)
    if years_max is not None:
        query = query.filter(Candidate.years_experience <= years_max)
    if location:
        query = query.filter(Candidate.location.ilike(f"%{location}%"))
    if current_company:
        query = query.filter(Candidate.current_company.ilike(f"%{current_company}%"))
    if education_level:
        query = query.join(Education).filter(Education.degree.ilike(f"%{education_level}%"))
    if skills:
        query = (
            query.join(CandidateSkill)
            .join(Skill)
            .filter(Skill.normalized_name.in_([s.lower() for s in skills]))
        )

    if q:
        like = f"%{q}%"
        filters = [
            Candidate.full_name.ilike(like),
            Candidate.current_company.ilike(like),
            Candidate.current_title.ilike(like),
            Candidate.summary.ilike(like),
        ]
        if "@" in q:
            filters.append(Candidate.email_hash == hash_value(q))
        query = query.filter(or_(*filters))

    results = query.offset(skip).limit(limit).all()
    return [CandidateRead.model_validate(c) for c in results]
