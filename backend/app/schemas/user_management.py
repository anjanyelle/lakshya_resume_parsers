from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserManagementRead(BaseModel):
    id: UUID
    email: EmailStr
    role: str
    is_active: bool
    tenant_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserManagementCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "recruiter"
    tenant_id: str = "default"


class UserManagementUpdate(BaseModel):
    email: EmailStr | None = None
    role: str | None = None
    is_active: bool | None = None


class RoleUpdate(BaseModel):
    role: str


class UserListResponse(BaseModel):
    users: list[UserManagementRead]
    total: int
