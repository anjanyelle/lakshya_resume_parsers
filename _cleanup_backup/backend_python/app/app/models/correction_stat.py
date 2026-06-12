from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CorrectionStat(Base):
    __tablename__ = "correction_stats"

    field_name: Mapped[str] = mapped_column(String(200), primary_key=True)
    correction_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
