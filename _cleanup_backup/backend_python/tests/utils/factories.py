from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.core.security import get_password_hash
from app.models import Candidate, ParsingJob, User
from app.models.candidate import CandidateStatus
from app.models.parsing_job import ParsingJobStatus


def make_user(email: str = "user@example.com", role: str = "admin") -> User:
    return User(
        id=uuid4(),
        email=email,
        hashed_password=get_password_hash("password123"),
        is_active=True,
        role=role,
        tenant_id="default",
    )


def make_candidate(full_name: str = "Jane Doe") -> Candidate:
    return Candidate(
        id=uuid4(),
        full_name=full_name,
        status=CandidateStatus.PENDING,
        tenant_id="default",
    )


def make_parsing_job(candidate_id) -> ParsingJob:
    return ParsingJob(
        id=uuid4(),
        candidate_id=candidate_id,
        filename="resume.pdf",
        file_path="s3://test-bucket/resume.pdf",
        status=ParsingJobStatus.PENDING,
        started_at=datetime.now(timezone.utc),
    )
