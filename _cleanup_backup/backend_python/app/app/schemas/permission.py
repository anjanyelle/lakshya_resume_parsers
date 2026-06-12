from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PermissionRead(BaseModel):
    id: UUID
    name: str
    description: str | None
    module: str
    created_at: datetime

    class Config:
        from_attributes = True


class RolePermissionRead(BaseModel):
    role: str
    permissions: list[PermissionRead]


class RolePermissionUpdate(BaseModel):
    permissions: list[str]


class PermissionListResponse(BaseModel):
    permissions: list[PermissionRead]
    total: int


class RolesResponse(BaseModel):
    roles: list[str]
