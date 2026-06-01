"""
Duplicate detection API endpoints for the Resume Parser API.

This module provides endpoints for detecting and managing duplicate candidates.
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_role
from app.models.user import User
from app.services.duplicate_detection import DuplicateDetectionService

router = APIRouter()
logger = logging.getLogger(__name__)


class MergeRequest(BaseModel):
    """Request model for merging candidates."""
    primary_candidate_id: str
    duplicate_candidate_ids: List[str]
    merge_strategy: str = "keep_newest"


class DuplicateCheckRequest(BaseModel):
    """Request model for checking duplicates on upload."""
    file_path: str
    email: Optional[str] = None
    phone: Optional[str] = None


@router.post("/check")
async def check_duplicates_on_upload(
    request: DuplicateCheckRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check for duplicates when uploading a new resume.
    
    Args:
        request: Duplicate check request with file path and contact info
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Duplicate check results
    """
    try:
        duplicate_service = DuplicateDetectionService(db)
        
        results = duplicate_service.check_duplicate_on_upload(
            file_path=request.file_path,
            email=request.email,
            phone=request.phone
        )
        
        return {
            "success": True,
            "results": results
        }
        
    except Exception as e:
        logger.exception("Error checking duplicates on upload")
        raise HTTPException(
            status_code=500,
            detail=f"Error checking duplicates: {str(e)}"
        )


@router.get("/candidates/{candidate_id}")
async def get_candidate_duplicates(
    candidate_id: UUID,
    similarity_threshold: float = Query(0.85, ge=0.0, le=1.0, description="Similarity threshold for fuzzy matching"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all duplicates for a specific candidate.
    
    Args:
        candidate_id: Candidate ID
        similarity_threshold: Minimum similarity score (0.0 to 1.0)
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        All duplicates for the candidate
    """
    try:
        duplicate_service = DuplicateDetectionService(db)
        
        # Get candidate to check for file hash
        from app.models.candidate import Candidate
        from app.models.parsing_job import ParsingJob
        
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        
        if not candidate:
            raise HTTPException(
                status_code=404,
                detail="Candidate not found"
            )
        
        # Get latest parsing job for file hash
        latest_job = db.query(ParsingJob).filter(
            ParsingJob.candidate_id == candidate_id
        ).order_by(ParsingJob.created_at.desc()).first()
        
        file_hash = latest_job.file_hash if latest_job else None
        
        duplicates = duplicate_service.find_all_duplicates(
            candidate_id=str(candidate_id),
            file_hash=file_hash,
            similarity_threshold=similarity_threshold
        )
        
        return {
            "success": True,
            "candidate_id": str(candidate_id),
            "duplicates": duplicates
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error getting candidate duplicates")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting duplicates: {str(e)}"
        )


@router.get("/candidates/{candidate_id}/hash")
async def get_duplicates_by_hash(
    candidate_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get duplicates by file hash for a candidate.
    
    Args:
        candidate_id: Candidate ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Duplicates found by file hash
    """
    try:
        from app.models.parsing_job import ParsingJob
        
        # Get latest parsing job for file hash
        latest_job = db.query(ParsingJob).filter(
            ParsingJob.candidate_id == candidate_id
        ).order_by(ParsingJob.created_at.desc()).first()
        
        if not latest_job or not latest_job.file_hash:
            return {
                "success": True,
                "candidate_id": str(candidate_id),
                "duplicates": [],
                "message": "No file hash found for this candidate"
            }
        
        duplicate_service = DuplicateDetectionService(db)
        duplicates = duplicate_service.find_duplicates_by_hash(
            latest_job.file_hash,
            exclude_candidate_id=str(candidate_id)
        )
        
        return {
            "success": True,
            "candidate_id": str(candidate_id),
            "file_hash": latest_job.file_hash,
            "duplicates": duplicates
        }
        
    except Exception as e:
        logger.exception("Error getting duplicates by hash")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting duplicates by hash: {str(e)}"
        )


@router.get("/candidates/{candidate_id}/email")
async def get_duplicates_by_email(
    candidate_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get duplicates by email for a candidate.
    
    Args:
        candidate_id: Candidate ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Duplicates found by email
    """
    try:
        from app.models.candidate import Candidate
        
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        
        if not candidate:
            raise HTTPException(
                status_code=404,
                detail="Candidate not found"
            )
        
        if not candidate.email:
            return {
                "success": True,
                "candidate_id": str(candidate_id),
                "duplicates": [],
                "message": "No email found for this candidate"
            }
        
        duplicate_service = DuplicateDetectionService(db)
        duplicates = duplicate_service.find_duplicates_by_email(
            candidate.email,
            exclude_candidate_id=str(candidate_id)
        )
        
        return {
            "success": True,
            "candidate_id": str(candidate_id),
            "email": candidate.email,
            "duplicates": duplicates
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error getting duplicates by email")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting duplicates by email: {str(e)}"
        )


@router.get("/candidates/{candidate_id}/phone")
async def get_duplicates_by_phone(
    candidate_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get duplicates by phone for a candidate.
    
    Args:
        candidate_id: Candidate ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Duplicates found by phone
    """
    try:
        from app.models.candidate import Candidate
        
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        
        if not candidate:
            raise HTTPException(
                status_code=404,
                detail="Candidate not found"
            )
        
        if not candidate.phone:
            return {
                "success": True,
                "candidate_id": str(candidate_id),
                "duplicates": [],
                "message": "No phone found for this candidate"
            }
        
        duplicate_service = DuplicateDetectionService(db)
        duplicates = duplicate_service.find_duplicates_by_phone(
            candidate.phone,
            exclude_candidate_id=str(candidate_id)
        )
        
        return {
            "success": True,
            "candidate_id": str(candidate_id),
            "phone": candidate.phone,
            "duplicates": duplicates
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error getting duplicates by phone")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting duplicates by phone: {str(e)}"
        )


@router.get("/candidates/{candidate_id}/fuzzy")
async def get_fuzzy_duplicates(
    candidate_id: UUID,
    similarity_threshold: float = Query(0.85, ge=0.0, le=1.0, description="Similarity threshold"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get fuzzy duplicates for a candidate.
    
    Args:
        candidate_id: Candidate ID
        similarity_threshold: Minimum similarity score (0.0 to 1.0)
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Fuzzy duplicates with similarity scores
    """
    try:
        from app.models.candidate import Candidate
        
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        
        if not candidate:
            raise HTTPException(
                status_code=404,
                detail="Candidate not found"
            )
        
        duplicate_service = DuplicateDetectionService(db)
        duplicates = duplicate_service.find_fuzzy_duplicates(
            candidate,
            similarity_threshold=similarity_threshold,
            exclude_candidate_id=str(candidate_id)
        )
        
        return {
            "success": True,
            "candidate_id": str(candidate_id),
            "similarity_threshold": similarity_threshold,
            "duplicates": duplicates
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error getting fuzzy duplicates")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting fuzzy duplicates: {str(e)}"
        )


@router.post("/merge")
async def merge_candidates(
    request: MergeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Merge duplicate candidates into a single candidate.
    
    Args:
        request: Merge request with primary and duplicate candidate IDs
        db: Database session
        current_user: Current authenticated user (admin only)
        
    Returns:
        Merge results
    """
    try:
        duplicate_service = DuplicateDetectionService(db)
        
        result = duplicate_service.merge_candidates(
            primary_candidate_id=request.primary_candidate_id,
            duplicate_candidate_ids=request.duplicate_candidate_ids,
            merge_strategy=request.merge_strategy
        )
        
        return {
            "success": True,
            "result": result
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.exception("Error merging candidates")
        raise HTTPException(
            status_code=500,
            detail=f"Error merging candidates: {str(e)}"
        )


@router.get("/stats")
async def get_duplicate_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get statistics about duplicate candidates in the system.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Duplicate statistics
    """
    try:
        from app.models.candidate import Candidate
        from app.models.parsing_job import ParsingJob
        
        total_candidates = db.query(Candidate).count()
        
        # Count candidates with duplicate emails
        from sqlalchemy import func
        duplicate_emails = db.query(
            func.count(Candidate.email)
        ).filter(
            Candidate.email.isnot(None)
        ).group_by(Candidate.email).having(
            func.count(Candidate.email) > 1
        ).count()
        
        # Count candidates with duplicate phones
        duplicate_phones = db.query(
            func.count(Candidate.phone)
        ).filter(
            Candidate.phone.isnot(None)
        ).group_by(Candidate.phone).having(
            func.count(Candidate.phone) > 1
        ).count()
        
        # Count candidates with duplicate file hashes
        duplicate_hashes = db.query(
            func.count(ParsingJob.file_hash)
        ).filter(
            ParsingJob.file_hash.isnot(None)
        ).group_by(ParsingJob.file_hash).having(
            func.count(ParsingJob.file_hash) > 1
        ).count()
        
        return {
            "success": True,
            "stats": {
                "total_candidates": total_candidates,
                "duplicate_email_groups": duplicate_emails,
                "duplicate_phone_groups": duplicate_phones,
                "duplicate_file_hash_groups": duplicate_hashes
            }
        }
        
    except Exception as e:
        logger.exception("Error getting duplicate stats")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting duplicate stats: {str(e)}"
        )
