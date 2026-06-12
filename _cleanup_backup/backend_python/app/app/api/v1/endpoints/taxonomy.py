from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import enforce_rate_limit, get_current_user, get_db
from app.data.skills.skills_master import SKILLS_DATABASE
from app.data.taxonomy.certifications_top import CERTIFICATION_ALIASES
from app.data.taxonomy.degree_taxonomy import DEGREE_ALIASES, DEGREE_KEYWORDS
from app.data.taxonomy.universities_top import TOP_UNIVERSITIES

router = APIRouter()


@router.get("/taxonomy/skills")
def taxonomy_skills(
    limit: int = Query(default=100, ge=1, le=500),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict[str, str | None]]:
    enforce_rate_limit(current_user.email, limit=60, per_seconds=60)
    results: list[dict[str, str | None]] = []
    for group, skills in SKILLS_DATABASE.items():
        for skill in skills:
            results.append(
                {
                    "name": skill.get("name"),
                    "category": skill.get("category") or group,
                    "synonyms": ", ".join(skill.get("synonyms", [])) or None,
                    "group": group,
                }
            )
            if len(results) >= limit:
                return results
    return results


@router.get("/taxonomy/degrees")
def taxonomy_degrees(
    limit: int = Query(default=100, ge=1, le=500),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict[str, str]]:
    enforce_rate_limit(current_user.email, limit=60, per_seconds=60)
    canonical = {value for value in DEGREE_ALIASES.values() if value}
    keywords = {value.title() for value in DEGREE_KEYWORDS if value}
    merged = sorted(canonical | keywords)
    return [{"name": value} for value in merged[:limit]]


@router.get("/taxonomy/universities")
def taxonomy_universities(
    limit: int = Query(default=100, ge=1, le=500),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict[str, str]]:
    enforce_rate_limit(current_user.email, limit=60, per_seconds=60)
    universities = sorted({name.title() for name in TOP_UNIVERSITIES})
    return [{"name": value} for value in universities[:limit]]


@router.get("/taxonomy/certifications")
def taxonomy_certifications(
    limit: int = Query(default=100, ge=1, le=500),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict[str, str]]:
    enforce_rate_limit(current_user.email, limit=60, per_seconds=60)
    values = sorted({value for value in CERTIFICATION_ALIASES.values() if value})
    return [{"name": value} for value in values[:limit]]
