import enum
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, Index, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ProficiencyLevel(str, enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"
    expert = "expert"


class CandidateSkill(Base):
    __tablename__ = "candidate_skills"
    __table_args__ = (
        Index("ix_candidate_skills_candidate_id", "candidate_id"),
        Index("ix_candidate_skills_skill_id", "skill_id"),
    )

    candidate_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        primary_key=True,
    )
    skill_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True,
    )
    proficiency_level: Mapped[ProficiencyLevel | None] = mapped_column(
        Enum(ProficiencyLevel, name="proficiency_level"), nullable=True
    )
    years_experience: Mapped[int | None] = mapped_column(Integer, nullable=True)

    candidate = relationship("Candidate", back_populates="candidate_skills")
    skill = relationship("Skill", back_populates="candidate_skills")
