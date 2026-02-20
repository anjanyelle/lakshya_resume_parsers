from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.candidate import CandidateStatus, ReviewStatus
from app.models.parsing_job import ParsingJobStatus
from app.schemas.candidate import (
    CandidateAchievementRead,
    CandidateSkillRead,
    CertificationRead,
    EducationRead,
    SkillRead,
    WorkHistoryRead,
)


class ParsingJobPublic(BaseModel):
    id: UUID
    candidate_id: UUID
    filename: str
    file_path: str
    original_file_copy_path: Optional[str] = None
    extracted_text_path: Optional[str] = None
    parsed_json_path: Optional[str] = None
    status: ParsingJobStatus = ParsingJobStatus.PENDING
    task_id: Optional[str] = None
    last_stage: Optional[str] = None
    confidence_score: Optional[float] = None
    ocr_confidence: Optional[float] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CandidatePublicRead(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime

    email: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    ssn: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    summary: Optional[str] = None
    years_experience: Optional[float] = None
    years_experience_confidence: Optional[float] = None
    current_title: Optional[str] = None
    current_company: Optional[str] = None
    status: CandidateStatus = CandidateStatus.PENDING
    consent_given: Optional[bool] = None
    consent_date: Optional[datetime] = None

    review_status: ReviewStatus | None = None
    review_assigned_to: str | None = None
    review_notes: str | None = None
    review_confidence: float | None = None

    work_history: List[WorkHistoryRead] = Field(default_factory=list)
    education: List[EducationRead] = Field(default_factory=list)
    skills: List[SkillRead] = Field(default_factory=list)
    candidate_skills: List[CandidateSkillRead] = Field(default_factory=list)
    parsing_jobs: List[ParsingJobPublic] = Field(default_factory=list)
    certifications: List[CertificationRead] = Field(default_factory=list)
    achievements: List[CandidateAchievementRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
