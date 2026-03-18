# Additional Models for Complete Resume JSON Format

from sqlalchemy import Column, String, Text, Date, ForeignKey, UUID, JSON, Integer, Float
from sqlalchemy.orm import relationship
from app.database import Base

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    name = Column(String(500), nullable=False)
    description = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    display_order = Column(Integer, default=0)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="projects")

class Publication(Base):
    __tablename__ = "publications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    name = Column(String(500), nullable=False)
    publisher = Column(String(500))
    description = Column(Text)
    publication_date = Column(Date)
    display_order = Column(Integer, default=0)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="publications")

class Volunteer(Base):
    __tablename__ = "volunteer_experience"
    
    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    organization = Column(String(500), nullable=False)
    role = Column(String(500))
    start_date = Column(Date)
    end_date = Column(Date)
    description = Column(Text)
    location = Column(String(500))
    display_order = Column(Integer, default=0)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="volunteer_experience")

class Award(Base):
    __tablename__ = "awards"
    
    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    name = Column(String(500), nullable=False)
    issuer = Column(String(500))
    description = Column(Text)
    award_date = Column(Date)
    display_order = Column(Integer, default=0)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="awards")

class Reference(Base):
    __tablename__ = "references"
    
    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    name = Column(String(500), nullable=False)
    company = Column(String(500))
    position = Column(String(500))
    email = Column(String(255))
    phone = Column(String(100))
    relationship = Column(String(200))
    display_order = Column(Integer, default=0)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="references")

class AdditionalText(Base):
    __tablename__ = "additional_texts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    content = Column(Text, nullable=False)
    section_type = Column(String(100))  # 'additional_info', 'custom_section', etc.
    display_order = Column(Integer, default=0)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="additional_texts")
