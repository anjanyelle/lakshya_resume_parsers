from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session
import random

from app.api.deps import enforce_rate_limit, get_current_user, get_db
from app.models.candidate import Candidate
from app.models.job_description import JobDescription
from app.models.match_score import MatchScore

router = APIRouter()

@router.post("/matching/job/{job_id}/candidates", response_model=dict)
def run_matching(
    job_id: UUID,
    limit: int = 20,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    enforce_rate_limit(current_user.email, limit=30, per_seconds=60)
    
    job = db.execute(select(JobDescription).where(JobDescription.id == job_id)).scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get all candidates
    candidates = db.execute(select(Candidate)).scalars().all()
    
    matches = []
    for idx, candidate in enumerate(candidates[:limit]):
        # Mock Matching Logic
        overall_score = random.uniform(60.0, 95.0)
        skill_score = random.uniform(60.0, 95.0)
        experience_score = random.uniform(50.0, 100.0)
        education_score = random.uniform(70.0, 100.0)
        
        # Upsert Match Score
        match_score = db.execute(
            select(MatchScore).where(
                MatchScore.job_id == job_id, 
                MatchScore.candidate_id == candidate.id
            )
        ).scalar_one_or_none()
        
        if not match_score:
            match_score = MatchScore(
                job_id=job_id,
                candidate_id=candidate.id
            )
            db.add(match_score)
            
        match_score.overall_score = overall_score
        match_score.skill_score = skill_score
        match_score.experience_score = experience_score
        match_score.education_score = education_score
        
        req_skills = job.required_skills or []
        req_skill_names = [s.get("skill_name") for s in req_skills if isinstance(s, dict)]
        
        match_score.matching_skills = req_skill_names[:2] if req_skill_names else ["Python", "SQL"]
        match_score.missing_skills = req_skill_names[2:] if req_skill_names and len(req_skill_names) > 2 else []
        match_score.extra_skills = ["AWS", "Docker"]
        match_score.experience_gap_years = 0.0
        
        if overall_score >= 85:
            match_score.recommendation = "Strong Match"
        elif overall_score >= 70:
            match_score.recommendation = "Good Match"
        else:
            match_score.recommendation = "Partial Match"
            
        match_score.reason = "Candidate matches core skills and experience requirements."
        
        db.commit()
        db.refresh(match_score)
        
        matches.append({
            "id": str(match_score.id),
            "job_id": str(job.id),
            "candidate_id": str(candidate.id),
            "candidate_name": candidate.full_name or "Unknown",
            "candidate_email": candidate.email or "",
            "candidate_location": candidate.location or "",
            "overall_score": float(match_score.overall_score),
            "skill_score": float(match_score.skill_score),
            "experience_score": float(match_score.experience_score),
            "education_score": float(match_score.education_score),
            "matching_skills": match_score.matching_skills,
            "missing_skills": match_score.missing_skills,
            "extra_skills": match_score.extra_skills,
            "experience_gap_years": float(match_score.experience_gap_years),
            "recommendation": match_score.recommendation,
            "reason": match_score.reason,
            "created_at": match_score.created_at.isoformat() if match_score.created_at else None,
        })
        
    return {
        "total_candidates": len(candidates),
        "matches": matches
    }

@router.get("/matching/job/{job_id}/results", response_model=dict)
def get_match_results(
    job_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    enforce_rate_limit(current_user.email, limit=100, per_seconds=60)
    
    match_scores = db.execute(
        select(MatchScore).where(MatchScore.job_id == job_id).order_by(MatchScore.overall_score.desc())
    ).scalars().all()
    
    matches = []
    for ms in match_scores:
        candidate = db.execute(select(Candidate).where(Candidate.id == ms.candidate_id)).scalar_one_or_none()
        if candidate:
            matches.append({
                "id": str(ms.id),
                "job_id": str(ms.job_id),
                "candidate_id": str(ms.candidate_id),
                "candidate_name": candidate.full_name or "Unknown",
                "candidate_email": candidate.email or "",
                "candidate_location": candidate.location or "",
                "overall_score": float(ms.overall_score),
                "skill_score": float(ms.skill_score),
                "experience_score": float(ms.experience_score),
                "education_score": float(ms.education_score),
                "matching_skills": ms.matching_skills,
                "missing_skills": ms.missing_skills,
                "extra_skills": ms.extra_skills,
                "experience_gap_years": float(ms.experience_gap_years),
                "recommendation": ms.recommendation,
                "reason": ms.reason,
                "created_at": ms.created_at.isoformat() if ms.created_at else None,
            })
            
    return {"matches": matches}

@router.get("/matching/results", response_model=dict)
def get_all_match_results(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    enforce_rate_limit(current_user.email, limit=100, per_seconds=60)
    
    match_scores = db.execute(
        select(MatchScore).order_by(MatchScore.overall_score.desc()).limit(100)
    ).scalars().all()
    
    matches = []
    for ms in match_scores:
        candidate = db.execute(select(Candidate).where(Candidate.id == ms.candidate_id)).scalar_one_or_none()
        if candidate:
            matches.append({
                "id": str(ms.id),
                "job_id": str(ms.job_id),
                "candidate_id": str(ms.candidate_id),
                "candidate_name": candidate.full_name or "Unknown",
                "candidate_email": candidate.email or "",
                "candidate_location": candidate.location or "",
                "overall_score": float(ms.overall_score),
                "skill_score": float(ms.skill_score),
                "experience_score": float(ms.experience_score),
                "education_score": float(ms.education_score),
                "matching_skills": ms.matching_skills,
                "missing_skills": ms.missing_skills,
                "extra_skills": ms.extra_skills,
                "experience_gap_years": float(ms.experience_gap_years),
                "recommendation": ms.recommendation,
                "reason": ms.reason,
                "created_at": ms.created_at.isoformat() if ms.created_at else None,
            })
            
    return {"matches": matches}
