import enum
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Enum, Float, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.encrypted_type import EncryptedString


class CandidateStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"


class ReviewStatus(str, enum.Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"


def _enum_values(enum_cls: type[enum.Enum]) -> list[str]:
    return [item.value for item in enum_cls]


class Candidate(Base):
    __tablename__ = "candidates"
    __table_args__ = (
        Index("ix_candidates_created_at", "created_at"),
        Index("ix_candidates_status", "status"),
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    email: Mapped[str | None] = mapped_column(
        EncryptedString(255), nullable=True
    )
    email_hash: Mapped[str | None] = mapped_column(
        String(64), index=True, nullable=True
    )
    full_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    phone: Mapped[str | None] = mapped_column(EncryptedString(50), nullable=True)
    ssn: Mapped[str | None] = mapped_column(EncryptedString(50), nullable=True)
    location: Mapped[str | None] = mapped_column(String(150), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    github_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary_manually_edited: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    years_experience: Mapped[float | None] = mapped_column(nullable=True)
    years_experience_confidence: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    current_title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    current_company: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[CandidateStatus] = mapped_column(
        Enum(
            CandidateStatus,
            name="candidate_status",
            values_callable=_enum_values,
        ),
        nullable=False,
        default=CandidateStatus.PENDING,
    )
    consent_given: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    consent_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    tenant_id: Mapped[str] = mapped_column(String(100), nullable=False, default="default")
    review_status: Mapped[ReviewStatus] = mapped_column(
        Enum(
            ReviewStatus,
            name="review_status",
            values_callable=_enum_values,
        ),
        nullable=False,
        default=ReviewStatus.PENDING,
    )
    review_assigned_to: Mapped[str | None] = mapped_column(String(255), nullable=True)
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    review_flagged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    review_confidence: Mapped[float | None] = mapped_column(nullable=True)
    review_flags: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    review_approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    review_approved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    review_rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    review_rejected_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    work_history = relationship(
        "WorkHistory", back_populates="candidate", cascade="all, delete-orphan"
    )
    education = relationship(
        "Education", back_populates="candidate", cascade="all, delete-orphan"
    )
    candidate_skills = relationship(
        "CandidateSkill", back_populates="candidate", cascade="all, delete-orphan"
    )
    skills = relationship("Skill", secondary="candidate_skills", viewonly=True)
    parsing_jobs = relationship(
        "ParsingJob", back_populates="candidate", cascade="all, delete-orphan"
    )
    certifications = relationship(
        "Certification", back_populates="candidate", cascade="all, delete-orphan"
    )

    achievements = relationship(
        "CandidateAchievement",
        back_populates="candidate",
        cascade="all, delete-orphan",
    )
