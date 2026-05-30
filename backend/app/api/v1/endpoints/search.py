from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.api.deps import enforce_rate_limit, get_current_user, get_db
from app.models import Candidate, CandidateSkill, Certification, Education, Skill, WorkHistory
from app.schemas.candidate import CandidateRead
from app.utils.pii import hash_value

router = APIRouter()


@router.get("/search", response_model=list[CandidateRead])
def advanced_search(
    skills: Optional[list[str]] = Query(default=None, description="Filter by candidate skills"),
    years_min: Optional[float] = Query(default=None, description="Minimum years of experience"),
    years_max: Optional[float] = Query(default=None, description="Maximum years of experience"),
    location: Optional[str] = Query(default=None, description="Filter by location"),
    current_company: Optional[str] = Query(default=None, description="Filter by current company (denormalized field)"),
    education_level: Optional[str] = Query(default=None, description="Filter by education level"),
    company: Optional[str] = Query(default=None, description="Search by company name in work history"),
    job_title: Optional[str] = Query(default=None, description="Search by job title in work history"),
    certification: Optional[str] = Query(default=None, description="Search by certification name"),
    salary_min: Optional[float] = Query(default=None, description="Minimum expected salary"),
    salary_max: Optional[float] = Query(default=None, description="Maximum expected salary"),
    q: Optional[str] = Query(default=None, description="Full-text search query"),
    skip: int = Query(default=0, ge=0, description="Number of results to skip"),
    limit: int = Query(default=50, ge=1, le=200, description="Number of results to return"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CandidateRead]:
    """
    Advanced candidate search with multiple filters.
    
    - **company**: Searches work_history.company_name (case-insensitive partial match)
    - **job_title**: Searches work_history.job_title (case-insensitive partial match)
    - **current_company**: Searches Candidate.current_company (denormalized field)
    - **certification**: Searches certifications.name (case-insensitive partial match)
    - **salary_min**: Filter by minimum expected_salary_min
    - **salary_max**: Filter by maximum expected_salary_max
    
    All filters are optional and can be combined.
    """
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
    
    # New: Search by company in work_history
    if company and company.strip():
        query = query.join(WorkHistory).filter(
            WorkHistory.company_name.ilike(f"%{company.strip()}%")
        )
    
    # New: Search by job_title in work_history
    if job_title and job_title.strip():
        query = query.join(WorkHistory).filter(
            WorkHistory.job_title.ilike(f"%{job_title.strip()}%")
        )
    
    # New: Search by certification name
    if certification and certification.strip():
        query = query.join(Certification).filter(
            Certification.name.ilike(f"%{certification.strip()}%")
        )
    
    # New: Filter by salary range
    if salary_min is not None:
        query = query.filter(Candidate.expected_salary_min >= salary_min)
    if salary_max is not None:
        query = query.filter(Candidate.expected_salary_max <= salary_max)

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
