from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ApiKeyCreate(BaseModel):
    subject: str
    role: str = "viewer"


class ApiKeyRead(BaseModel):
    id: UUID
    subject: str
    role: str
    created_at: datetime
    revoked_at: datetime | None

    model_config = {"from_attributes": True}


class ApiKeyResponse(BaseModel):
    api_key: str
    key_id: UUID
