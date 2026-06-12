from __future__ import annotations

import sys
import os
import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, Query, HTTPException, Body
from sqlalchemy import desc, select
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.deps import enforce_rate_limit, get_current_user, get_db
from app.models import Candidate, Correction

router = APIRouter()


class UserCorrectionRequest(BaseModel):
    """Request model for user corrections."""
    field: str
    wrong_value: str
    correct_value: str


@router.post("/parse/{parse_id}/correct")
def submit_user_correction(
    parse_id: str,
    correction_data: UserCorrectionRequest = Body(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """
    Submit a user correction for a parsed resume.
    
    This endpoint captures user corrections to improve future parsing accuracy.
    """
    enforce_rate_limit(current_user.email, limit=30, per_seconds=60)
    
    try:
        # Try to use the feedback store from the AI service
        ai_service_path = find_ai_service_path()
        if ai_service_path:
            sys.path.insert(0, str(ai_service_path))
            
            try:
                from parsers.master_parser import MasterParser
                
                # Initialize master parser and save correction
                parser = MasterParser()
                success = parser.save_user_correction(
                    parse_id,
                    correction_data.field,
                    correction_data.wrong_value,
                    correction_data.correct_value
                )
                
                if success:
                    return {"message": "Correction saved successfully", "status": "success"}
                else:
                    raise HTTPException(status_code=500, detail="Failed to save correction")
                    
            except ImportError:
                # Fallback to database storage if AI service not available
                return save_correction_to_database(
                    db, current_user, parse_id, correction_data
                )
            finally:
                # Remove the path to avoid conflicts
                if str(ai_service_path) in sys.path:
                    sys.path.remove(str(ai_service_path))
        else:
            # Fallback to database storage
            return save_correction_to_database(
                db, current_user, parse_id, correction_data
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save correction: {str(e)}")


def find_ai_service_path() -> Path | None:
    """Find the AI service path."""
    current_dir = Path(__file__).parent.parent.parent.parent.parent
    ai_service_path = current_dir / "ai-service"
    
    if ai_service_path.exists() and (ai_service_path / "parsers").exists():
        return ai_service_path
    return None


def save_correction_to_database(
    db: Session, 
    current_user, 
    parse_id: str, 
    correction_data: UserCorrectionRequest
) -> dict[str, str]:
    """Fallback method to save correction to database."""
    try:
        # Create a database correction record
        correction = Correction(
            candidate_id=parse_id,  # Using parse_id as fallback
            field_name=correction_data.field,
            original_value=correction_data.wrong_value,
            corrected_value=correction_data.correct_value,
            corrected_by=current_user.email,
            corrected_at=datetime.datetime.utcnow()
        )
        
        db.add(correction)
        db.commit()
        
        return {"message": "Correction saved to database", "status": "success"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save to database: {str(e)}")


@router.get("/corrections/recent")
def recent_corrections(
    limit: int = Query(default=50, ge=1, le=200),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict[str, str | None]]:
    enforce_rate_limit(current_user.email, limit=60, per_seconds=60)
    try:
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
    except ProgrammingError as e:
        err_msg = str(getattr(e, "orig", e) or e).lower()
        if "corrections" in err_msg or "candidates" in err_msg or "does not exist" in err_msg:
            db.rollback()
            return []
        raise
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
