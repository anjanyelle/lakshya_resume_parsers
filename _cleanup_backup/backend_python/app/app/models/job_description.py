from __future__ import annotations

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models.base import Base

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    department = Column(String(255), nullable=True)
    min_experience_years = Column(Integer, nullable=True)
    max_experience_years = Column(Integer, nullable=True)
    education_requirement = Column(String(255), nullable=True)
    employment_type = Column(String(100), nullable=True)
    seniority_level = Column(String(100), nullable=True)
    location = Column(String(255), nullable=True)
    salary_range = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False, server_default="active")
    required_skills = Column(JSONB, default=list)
    preferred_skills = Column(JSONB, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
