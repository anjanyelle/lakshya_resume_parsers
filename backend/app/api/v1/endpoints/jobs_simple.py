#!/usr/bin/env python3
"""
Simple job status endpoint that works with string UUIDs
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.api.deps import get_current_user, get_db
from app.core.database import SessionLocal

router = APIRouter()

@router.get("/jobs-simple/{job_id}/status")
def job_status_simple(
    job_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Simple job status endpoint using raw SQL"""
    try:
        # Use raw SQL to avoid UUID issues
        result = db.execute(
            text("SELECT id, status, last_stage, error_message FROM parsing_jobs WHERE id = :job_id"),
            {"job_id": job_id}
        ).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "job_id": result[0],
            "status": result[1],
            "last_stage": result[2],
            "error_message": result[3]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
