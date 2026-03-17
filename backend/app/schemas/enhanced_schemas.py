# Enhanced Schemas for Complete Resume JSON Format

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field

# Basic Info Schema
class BasicsBase(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    titleBeforeName: Optional[str] = None
    titleAfterName: Optional[str] = None
    dateOfBirth: Optional[date] = None
    phone: Optional[List[str]] = Field(default_factory=list)
    email: Optional[List[str]] = Field(default_factory=list)
    web: Optional[List[str]] = Field(default_factory=list)
    street: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    postal: Optional[str] = None

class BasicsRead(BasicsBase):
    candidate_id: UUID
    
    model_config = ConfigDict(from_attributes=True)

# Project Schema
class ProjectBase(BaseModel):
    name: str = Field(..., max_length=500)
    description: Optional[str] = None
    startDate: Optional[date] = None
    endDate: Optional[date] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = None
    startDate: Optional[date] = None
    endDate: Optional[date] = None

class ProjectRead(ProjectBase):
    id: UUID
    candidate_id: UUID
    
    model_config = ConfigDict(from_attributes=True)

# Publication Schema
class PublicationBase(BaseModel):
    name: str = Field(..., max_length=500)
    publisher: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = None
    publicationDate: Optional[date] = None

class PublicationCreate(PublicationBase):
    pass

class PublicationUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=500)
    publisher: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = None
    publicationDate: Optional[date] = None

class PublicationRead(PublicationBase):
    id: UUID
    candidate_id: UUID
    
    model_config = ConfigDict(from_attributes=True)

# Volunteer Schema
class VolunteerBase(BaseModel):
    organization: str = Field(..., max_length=500)
    role: Optional[str] = Field(default=None, max_length=500)
    startDate: Optional[date] = None
    endDate: Optional[date] = None
    description: Optional[str] = None
    location: Optional[str] = Field(default=None, max_length=500)

class VolunteerCreate(VolunteerBase):
    pass

class VolunteerUpdate(BaseModel):
    organization: Optional[str] = Field(default=None, max_length=500)
    role: Optional[str] = Field(default=None, max_length=500)
    startDate: Optional[date] = None
    endDate: Optional[date] = None
    description: Optional[str] = None
    location: Optional[str] = Field(default=None, max_length=500)

class VolunteerRead(VolunteerBase):
    id: UUID
    candidate_id: UUID
    
    model_config = ConfigDict(from_attributes=True)

# Award Schema
class AwardBase(BaseModel):
    name: str = Field(..., max_length=500)
    issuer: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = None
    awardDate: Optional[date] = None

class AwardCreate(AwardBase):
    pass

class AwardUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=500)
    issuer: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = None
    awardDate: Optional[date] = None

class AwardRead(AwardBase):
    id: UUID
    candidate_id: UUID
    
    model_config = ConfigDict(from_attributes=True)

# Reference Schema
class ReferenceBase(BaseModel):
    name: str = Field(..., max_length=500)
    company: Optional[str] = Field(default=None, max_length=500)
    position: Optional[str] = Field(default=None, max_length=500)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=100)
    relationship: Optional[str] = Field(default=None, max_length=200)

class ReferenceCreate(ReferenceBase):
    pass

class ReferenceUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=500)
    company: Optional[str] = Field(default=None, max_length=500)
    position: Optional[str] = Field(default=None, max_length=500)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=100)
    relationship: Optional[str] = Field(default=None, max_length=200)

class ReferenceRead(ReferenceBase):
    id: UUID
    candidate_id: UUID
    
    model_config = ConfigDict(from_attributes=True)

# Additional Text Schema
class AdditionalTextBase(BaseModel):
    content: str
    section_type: Optional[str] = Field(default=None, max_length=100)

class AdditionalTextCreate(AdditionalTextBase):
    pass

class AdditionalTextUpdate(BaseModel):
    content: Optional[str] = None
    section_type: Optional[str] = Field(default=None, max_length=100)

class AdditionalTextRead(AdditionalTextBase):
    id: UUID
    candidate_id: UUID
    
    model_config = ConfigDict(from_attributes=True)

# Complete Resume JSON Schema
class CompleteResumeJSON(BaseModel):
    basics: Optional[BasicsBase] = None
    profile: Optional[str] = None
    work: Optional[List[dict]] = Field(default_factory=list)
    education: Optional[List[dict]] = Field(default_factory=list)
    projects: Optional[List[ProjectBase]] = Field(default_factory=list)
    volunteer: Optional[List[VolunteerBase]] = Field(default_factory=list)
    skills: Optional[List[dict]] = Field(default_factory=list)
    certifications: Optional[List[dict]] = Field(default_factory=list)
    publications: Optional[List[PublicationBase]] = Field(default_factory=list)
    awards: Optional[List[AwardBase]] = Field(default_factory=list)
    achievements: Optional[List[dict]] = Field(default_factory=list)
    hobbies: Optional[List[str]] = Field(default_factory=list)
    references: Optional[List[ReferenceBase]] = Field(default_factory=list)
    texts: Optional[List[AdditionalTextBase]] = Field(default_factory=list)

# Enhanced Candidate Schema
class EnhancedCandidateBase(BaseModel):
    # Existing fields
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    summary: Optional[str] = None
    years_experience: Optional[float] = None
    years_experience_confidence: Optional[float] = None
    current_title: Optional[str] = None
    current_company: Optional[str] = None
    
    # New fields for target JSON
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title_before_name: Optional[str] = None
    title_after_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    street: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    postal: Optional[str] = None
    web: Optional[List[str]] = Field(default_factory=list)
    profile: Optional[str] = None
    hobbies: Optional[List[str]] = Field(default_factory=list)

class EnhancedCandidateRead(EnhancedCandidateBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    # All relationships
    work_history: List[dict] = Field(default_factory=list)
    education: List[dict] = Field(default_factory=list)
    skills: List[dict] = Field(default_factory=list)
    certifications: List[dict] = Field(default_factory=list)
    achievements: List[dict] = Field(default_factory=list)
    projects: List[ProjectRead] = Field(default_factory=list)
    publications: List[PublicationRead] = Field(default_factory=list)
    volunteer_experience: List[VolunteerRead] = Field(default_factory=list)
    awards: List[AwardRead] = Field(default_factory=list)
    references: List[ReferenceRead] = Field(default_factory=list)
    additional_texts: List[AdditionalTextRead] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)
