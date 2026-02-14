from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import Candidate, ParsingJob
from app.models.candidate import CandidateStatus
from app.models.parsing_job import ParsingJobStatus


def seed_candidate_with_job(db: Session) -> Candidate:
    candidate = Candidate(full_name="Scenario User", tenant_id="default")
    db.add(candidate)
    db.flush()
    job = ParsingJob(
        candidate_id=candidate.id,
        filename="scenario.pdf",
        file_path="s3://test-bucket/scenario.pdf",
        status=ParsingJobStatus.PENDING,
    )
    db.add(job)
    db.commit()
    db.refresh(candidate)
    return candidate


def seed_failed_job(db: Session) -> ParsingJob:
    candidate = Candidate(full_name="Failed Job", tenant_id="default")
    db.add(candidate)
    db.flush()
    job = ParsingJob(
        candidate_id=candidate.id,
        filename="failed.pdf",
        file_path="s3://test-bucket/failed.pdf",
        status=ParsingJobStatus.FAILED,
        error_message="Parsing error",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job
