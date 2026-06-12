from __future__ import annotations

import uuid
from sqlalchemy import Column, Float, DateTime, ForeignKey, String, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models.base import Base

class MatchScore(Base):
    __tablename__ = "match_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False)
    
    overall_score = Column(Float, nullable=False, default=0.0)
    skill_score = Column(Float, nullable=False, default=0.0)
    experience_score = Column(Float, nullable=False, default=0.0)
    education_score = Column(Float, nullable=False, default=0.0)
    
    matching_skills = Column(JSONB, default=list)
    missing_skills = Column(JSONB, default=list)
    extra_skills = Column(JSONB, default=list)
    
    experience_gap_years = Column(Float, default=0.0)
    recommendation = Column(String(50), nullable=True)
    reason = Column(String(1000), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # candidate = relationship("Candidate", back_populates="matches")
    # job = relationship("JobDescription")
