from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.candidate import CandidateStatus
from app.models.candidate import ReviewStatus
from app.models.candidate_skill import ProficiencyLevel
from app.models.parsing_job import ParsingJobStatus


class WorkHistoryBase(BaseModel):
    company_name: Optional[str] = None
    client_name: Optional[str] = None
    job_title: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None
    location: Optional[str] = None
    description: Optional[str] = None
    display_order: Optional[int] = None


class WorkHistoryCreate(WorkHistoryBase):
    pass


class WorkHistoryUpdate(WorkHistoryBase):
    pass


class WorkHistoryRead(WorkHistoryBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class EducationBase(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    gpa: Optional[float] = None
    description: Optional[str] = None


class EducationCreate(EducationBase):
    pass


class EducationUpdate(EducationBase):
    pass


class EducationRead(EducationBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class SkillBase(BaseModel):
    name: str = Field(..., max_length=150)
    category: Optional[str] = Field(default=None, max_length=100)
    normalized_name: Optional[str] = Field(default=None, max_length=150)


class SkillCreate(SkillBase):
    pass


class SkillUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=150)
    category: Optional[str] = Field(default=None, max_length=100)
    normalized_name: Optional[str] = Field(default=None, max_length=150)


class SkillRead(SkillBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class CandidateSkillBase(BaseModel):
    skill_id: UUID
    proficiency_level: Optional[ProficiencyLevel] = None
    years_experience: Optional[int] = None


class CandidateSkillCreate(CandidateSkillBase):
    pass


class CandidateSkillUpdate(BaseModel):
    proficiency_level: Optional[ProficiencyLevel] = None
    years_experience: Optional[int] = None


class CandidateSkillRead(CandidateSkillBase):
    skill: Optional[SkillRead] = None

    model_config = ConfigDict(from_attributes=True)


class ParsingJobBase(BaseModel):
    filename: str
    file_path: str
    original_file_copy_path: Optional[str] = None
    extracted_text_path: Optional[str] = None
    parsed_json_path: Optional[str] = None
    status: ParsingJobStatus = ParsingJobStatus.PENDING
    task_id: Optional[str] = None
    last_stage: Optional[str] = None
    raw_text: Optional[str] = None
    parsed_data: Optional[dict] = None
    confidence_score: Optional[float] = None
    ocr_confidence: Optional[float] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ParsingJobRead(ParsingJobBase):
    id: UUID
    candidate_id: UUID

    model_config = ConfigDict(from_attributes=True)


class CertificationBase(BaseModel):
    name: str = Field(..., max_length=200)
    issuing_organization: Optional[str] = Field(default=None, max_length=200)
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    credential_id: Optional[str] = Field(default=None, max_length=100)


class CertificationCreate(CertificationBase):
    pass


class CertificationUpdate(CertificationBase):
    pass


class CertificationRead(CertificationBase):
    id: UUID
    candidate_id: UUID

    model_config = ConfigDict(from_attributes=True)


class CandidateAchievementBase(BaseModel):
    title: str
    year: Optional[int] = None
    confidence: Optional[float] = None


class CandidateAchievementRead(CandidateAchievementBase):
    id: UUID
    candidate_id: UUID

    model_config = ConfigDict(from_attributes=True)


class CandidateBase(BaseModel):
    email: Optional[EmailStr] = None
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


class CandidateCreate(CandidateBase):
    pass


class CandidateUpdate(BaseModel):
    email: Optional[EmailStr] = None
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
    status: Optional[CandidateStatus] = None
    consent_given: Optional[bool] = None
    consent_date: Optional[datetime] = None


class CandidateRead(CandidateBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    review_status: ReviewStatus | None = None
    review_assigned_to: str | None = None
    review_notes: str | None = None
    review_confidence: float | None = None
    work_history: List[WorkHistoryRead] = Field(default_factory=list)
    education: List[EducationRead] = Field(default_factory=list)
    skills: List[SkillRead] = Field(default_factory=list)
    candidate_skills: List[CandidateSkillRead] = Field(default_factory=list)
    parsing_jobs: List[ParsingJobRead] = Field(default_factory=list)
    certifications: List[CertificationRead] = Field(default_factory=list)
    achievements: List[CandidateAchievementRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
