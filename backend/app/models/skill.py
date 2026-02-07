from uuid import UUID, uuid4

from sqlalchemy import Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Skill(Base):
    __tablename__ = "skills"
    __table_args__ = (Index("ix_skills_normalized_name", "normalized_name"),)

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    normalized_name: Mapped[str | None] = mapped_column(String(150), nullable=True)

    candidate_skills = relationship("CandidateSkill", back_populates="skill")
