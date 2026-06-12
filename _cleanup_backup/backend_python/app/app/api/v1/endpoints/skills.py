from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import distinct
from sqlalchemy.orm import Session

from app.api.deps import enforce_rate_limit, get_current_user, get_db
from app.models import Skill

router = APIRouter()


@router.get("/skills")
def list_skills(
    q: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict[str, str | None]]:
    enforce_rate_limit(current_user.email, limit=60, per_seconds=60)
    query = db.query(Skill)
    if q:
        query = query.filter(Skill.name.ilike(f"%{q}%"))
    skills = query.offset(skip).limit(limit).all()
    return [
        {"name": skill.name, "category": skill.category, "normalized_name": skill.normalized_name}
        for skill in skills
    ]


@router.get("/skills/categories")
def skill_categories(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[str]:
    enforce_rate_limit(current_user.email, limit=60, per_seconds=60)
    rows = db.query(distinct(Skill.category)).filter(Skill.category.isnot(None)).all()
    return [row[0] for row in rows if row[0]]
