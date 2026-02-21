from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from app.models.candidate import ReviewStatus
from app.schemas.candidate import CandidateRead, ParsingJobRead


class CorrectionItem(BaseModel):
    field_name: str
    original_value: str | None = None
    corrected_value: str | None = None


class CorrectionRequest(BaseModel):
    corrections: list[CorrectionItem]
    review_notes: str | None = None
    review_status: ReviewStatus | None = None
    review_assigned_to: str | None = None


class CorrectionRead(BaseModel):
    id: UUID
    candidate_id: UUID
    field_name: str
    original_value: str | None
    corrected_value: str | None
    corrected_by: str | None
    corrected_at: datetime

    model_config = {"from_attributes": True}


class ReviewFlags(BaseModel):
    overall_confidence: float | None = None
    flagged_fields: dict[str, float]
    discrepancies: list[str]
    rule_flags: list[str] = []


class CandidateReviewResponse(BaseModel):
    candidate: CandidateRead
    latest_job: ParsingJobRead | None = None
    review_flags: ReviewFlags
    suggested_corrections: dict[str, Any] | None = None


class ReviewQueueItem(BaseModel):
    candidate: CandidateRead
    confidence: float | None
    review_status: ReviewStatus
    review_assigned_to: str | None


class CorrectionAnalytics(BaseModel):
    most_corrected_fields: list[dict[str, Any]]
    corrections_over_time: list[dict[str, Any]]
    reviewer_performance: list[dict[str, Any]]
