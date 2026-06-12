from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class JobBase(BaseModel):
    title: str
    description: Optional[str] = None
    department: Optional[str] = None
    min_experience_years: Optional[int] = None
    max_experience_years: Optional[int] = None
    education_requirement: Optional[str] = None
    employment_type: Optional[str] = None
    seniority_level: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    status: Optional[str] = "active"
    required_skills: Optional[List[Dict[str, Any]]] = None
    preferred_skills: Optional[List[Dict[str, Any]]] = None

class JobCreate(JobBase):
    pass

class JobUpdate(JobBase):
    title: Optional[str] = None

class JobResponse(JobBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
