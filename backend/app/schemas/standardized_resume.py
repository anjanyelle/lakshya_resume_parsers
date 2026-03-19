from datetime import date, datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class CompanySchema(BaseModel):
    name: str
    client_flag: bool = False
    company_id: Optional[str] = None
    industry: Optional[str] = None

class LocationSchema(BaseModel):
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    remote: bool = False

EmploymentType = Literal[
    "full_time", "part_time", "contract", "internship", "freelance", "temporary"
]

class WorkHistoryItem(BaseModel):
    id: str
    person_id: str
    role: str
    company: CompanySchema
    location: LocationSchema
    start_date: date
    end_date: Optional[date] = None
    currently_working: bool = False
    employment_type: Optional[EmploymentType] = None
    description: str
    bullets: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    raw_text: str
    confidence_score: float = 0.0
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class StandardizedWorkHistory(BaseModel):
    work_history: List[WorkHistoryItem]
