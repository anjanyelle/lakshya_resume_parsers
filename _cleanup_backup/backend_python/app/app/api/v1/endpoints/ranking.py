"""
Ranking API endpoints for the Resume Parser API.

This module provides endpoints for ranking and sorting candidates
based on various criteria including match scores, skills, experience, etc.
"""

import logging
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_role
from app.models.user import User
from app.services.ranking import RankingService, RankingCriteria

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/candidates/rank")
async def rank_candidates(
    job_id: Optional[str] = Query(None, description="Job ID for job-specific matching"),
    criteria: RankingCriteria = Query(
        RankingCriteria.MATCH_SCORE,
        description="Ranking criteria to use"
    ),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of candidates"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    status: Optional[str] = Query(None, description="Filter by candidate status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Rank candidates based on specified criteria.
    
    Args:
        job_id: Job ID for job-specific matching (optional)
        criteria: Ranking criteria (match_score, skills_match, experience, confidence, recency, review_status)
        limit: Maximum number of candidates to return (1-1000)
        offset: Offset for pagination
        status: Filter by candidate status (optional)
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of ranked candidates with scores and metadata
    """
    try:
        ranking_service = RankingService(db)
        
        # Convert status string to enum if provided
        from app.models.candidate import CandidateStatus
        status_filter = None
        if status:
            try:
                status_filter = CandidateStatus(status)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status: {status}"
                )
        
        ranked_candidates = ranking_service.rank_candidates(
            job_id=job_id,
            criteria=criteria,
            limit=limit,
            offset=offset,
            status_filter=status_filter
        )
        
        return {
            "success": True,
            "count": len(ranked_candidates),
            "criteria": criteria.value,
            "job_id": job_id,
            "candidates": ranked_candidates
        }
        
    except Exception as e:
        logger.exception("Error ranking candidates")
        raise HTTPException(
            status_code=500,
            detail=f"Error ranking candidates: {str(e)}"
        )


@router.get("/candidates/top")
async def get_top_candidates(
    job_id: Optional[str] = Query(None, description="Job ID for job-specific matching"),
    limit: int = Query(10, ge=1, le=100, description="Number of top candidates"),
    criteria: RankingCriteria = Query(
        RankingCriteria.MATCH_SCORE,
        description="Ranking criteria to use"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get top N candidates based on ranking criteria.
    
    Args:
        job_id: Job ID for job-specific matching (optional)
        limit: Number of top candidates to return (1-100)
        criteria: Ranking criteria to use
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of top candidates
    """
    try:
        ranking_service = RankingService(db)
        
        top_candidates = ranking_service.get_top_candidates(
            job_id=job_id,
            limit=limit,
            criteria=criteria
        )
        
        return {
            "success": True,
            "count": len(top_candidates),
            "criteria": criteria.value,
            "job_id": job_id,
            "candidates": top_candidates
        }
        
    except Exception as e:
        logger.exception("Error getting top candidates")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting top candidates: {str(e)}"
        )


@router.get("/candidates/ranking/summary")
async def get_ranking_summary(
    job_id: Optional[str] = Query(None, description="Job ID for job-specific matching"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get summary statistics for candidate rankings.
    
    Args:
        job_id: Job ID for job-specific matching (optional)
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Ranking summary statistics
    """
    try:
        ranking_service = RankingService(db)
        
        summary = ranking_service.get_ranking_summary(job_id=job_id)
        
        return {
            "success": True,
            "job_id": job_id,
            "summary": summary
        }
        
    except Exception as e:
        logger.exception("Error getting ranking summary")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting ranking summary: {str(e)}"
        )


@router.get("/candidates/{candidate_id}/score")
async def get_candidate_score(
    candidate_id: UUID,
    job_id: Optional[str] = Query(None, description="Job ID for job-specific matching"),
    criteria: RankingCriteria = Query(
        RankingCriteria.MATCH_SCORE,
        description="Ranking criteria to use"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get ranking score for a specific candidate.
    
    Args:
        candidate_id: Candidate ID
        job_id: Job ID for job-specific matching (optional)
        criteria: Ranking criteria to use
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Candidate ranking score and breakdown
    """
    try:
        from app.models.candidate import Candidate
        
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        
        if not candidate:
            raise HTTPException(
                status_code=404,
                detail="Candidate not found"
            )
        
        ranking_service = RankingService(db)
        score_data = ranking_service._calculate_ranking_score(
            candidate,
            criteria,
            job_id
        )
        
        return {
            "success": True,
            "candidate_id": str(candidate_id),
            "criteria": criteria.value,
            "job_id": job_id,
            "score": score_data["score"],
            "breakdown": score_data["breakdown"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error getting candidate score")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting candidate score: {str(e)}"
        )
