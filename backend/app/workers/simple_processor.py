#!/usr/bin/env python3
"""
Simple synchronous resume processor for development
"""
import logging
from pathlib import Path
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import SessionLocal
from app.models.parsing_job import ParsingJob, ParsingJobStatus
from app.models.candidate import Candidate, CandidateStatus
from app.services.parser.simple_parser import SimpleResumeParser
from sqlalchemy import text

logger = logging.getLogger(__name__)

def process_resume_sync(job_id: str) -> bool:
    """Process a resume synchronously without Celery"""
    logger.info(f"Starting synchronous processing for job: {job_id}")
    
    db = SessionLocal()
    try:
        # Load the job using raw SQL to avoid UUID issues
        job = db.execute(
            text("SELECT id, candidate_id, filename, file_path FROM parsing_jobs WHERE id = :job_id"),
            {"job_id": job_id}
        ).fetchone()
        
        if not job:
            logger.error(f"Job not found: {job_id}")
            return False
        
        # Update job status to processing
        db.execute(
            text("UPDATE parsing_jobs SET status = :status, started_at = datetime('now') WHERE id = :job_id"),
            {"status": "processing", "job_id": job_id}
        )
        db.commit()
        
        # Get file path
        file_path = job[3]  # file_path column
        if not file_path or not Path(file_path).exists():
            logger.error(f"File not found: {file_path}")
            db.execute(
                text("UPDATE parsing_jobs SET status = :status, error_message = :error, completed_at = datetime('now') WHERE id = :job_id"),
                {"status": "failed", "error": "File not found", "job_id": job_id}
            )
            db.commit()
            return False
        
        # Simple text extraction and parsing
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            except Exception as e:
                logger.error(f"Failed to read file: {e}")
                db.execute(
                    text("UPDATE parsing_jobs SET status = :status, error_message = :error, completed_at = datetime('now') WHERE id = :job_id"),
                    {"status": "failed", "error": f"Failed to read file: {str(e)}", "job_id": job_id}
                )
                db.commit()
                return False
        
        # Simple parsing
        parser = SimpleResumeParser()
        parsed_data = parser.parse(content)
        
        # Create or update candidate
        candidate_id = job[2]  # candidate_id column
        if candidate_id:
            # Update existing candidate
            db.execute(
                text("UPDATE candidates SET full_name = :name, summary = :summary, status = :status, updated_at = datetime('now') WHERE id = :candidate_id"),
                {
                    "name": parsed_data.get('full_name', ''),
                    "summary": parsed_data.get('summary', ''),
                    "status": 'success',
                    "candidate_id": candidate_id
                }
            )
        
        # Update job with results
        db.execute(
            text("UPDATE parsing_jobs SET status = :status, raw_text = :raw_text, parsed_data = :parsed_data, confidence_score = :confidence, completed_at = datetime('now') WHERE id = :job_id"),
            {
                "status": "success",
                "raw_text": content,
                "parsed_data": str(parsed_data),
                "confidence": 0.8,
                "job_id": job_id
            }
        )
        db.commit()
        
        logger.info(f"Successfully processed job: {job_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {e}")
        db.execute(
            text("UPDATE parsing_jobs SET status = :status, error_message = :error, completed_at = datetime('now') WHERE id = :job_id"),
            {"status": "failed", "error": str(e), "job_id": job_id}
        )
        db.commit()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        process_resume_sync(sys.argv[1])
