from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import enforce_rate_limit_request, get_current_user, get_db, require_role
from app.core.security import get_password_hash
from app.crud.user import user as user_crud
from app.models import User
from app.schemas.user_management import (
    RoleUpdate,
    UserManagementCreate,
    UserManagementRead,
    UserManagementUpdate,
    UserListResponse,
)
from app.utils.audit import log_audit

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/users", response_model=UserListResponse)
def list_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> UserListResponse:
    """List all users (admin only)."""
    users = user_crud.get_multi(db, skip=skip, limit=limit)
    total = user_crud.count(db)
    return UserListResponse(users=users, total=total)


@router.get("/users/{user_id}", response_model=UserManagementRead)
def get_user(
    user_id: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> UserManagementRead:
    """Get user details (admin only)."""
    user = user_crud.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserManagementRead.model_validate(user)


@router.post("/users", response_model=UserManagementRead)
def create_user(
    payload: UserManagementCreate,
    request: Request,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> UserManagementRead:
    """Create a new user (admin only)."""
    enforce_rate_limit_request(request, limit=10, per_seconds=60)
    
    existing = user_crud.get_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = user_crud.create(
        db,
        {
            "email": payload.email,
            "hashed_password": get_password_hash(payload.password),
            "role": payload.role,
            "is_active": True,
            "tenant_id": payload.tenant_id,
        },
    )
    
    try:
        log_audit(
            db,
            user_id=str(current_user.id),
            action="create_user",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=request.client.host if request.client else None,
            details={"target_email": user.email, "role": user.role},
        )
    except Exception as e:
        logger.warning("Audit log failed (create_user still succeeded): %s", e)
        db.rollback()
    
    return UserManagementRead.model_validate(user)


@router.put("/users/{user_id}", response_model=UserManagementRead)
def update_user(
    user_id: str,
    payload: UserManagementUpdate,
    request: Request,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> UserManagementRead:
    """Update user details (admin only)."""
    user = user_crud.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = payload.model_dump(exclude_unset=True)
    if "email" in update_data and update_data["email"] != user.email:
        existing = user_crud.get_by_email(db, update_data["email"])
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    updated_user = user_crud.update(db, db_obj=user, obj_in=update_data)
    
    try:
        log_audit(
            db,
            user_id=str(current_user.id),
            action="update_user",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=request.client.host if request.client else None,
            details={"changes": update_data},
        )
    except Exception as e:
        logger.warning("Audit log failed (update_user still succeeded): %s", e)
        db.rollback()
    
    return UserManagementRead.model_validate(updated_user)


@router.delete("/users/{user_id}")
def delete_user(
    user_id: str,
    request: Request,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Delete a user (admin only)."""
    user = user_crud.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    user_crud.remove(db, id=user_id)
    
    try:
        log_audit(
            db,
            user_id=str(current_user.id),
            action="delete_user",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=request.client.host if request.client else None,
            details={"deleted_email": user.email},
        )
    except Exception as e:
        logger.warning("Audit log failed (delete_user still succeeded): %s", e)
        db.rollback()
    
    return {"status": "ok"}


@router.put("/users/{user_id}/role", response_model=UserManagementRead)
def update_user_role(
    user_id: str,
    payload: RoleUpdate,
    request: Request,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> UserManagementRead:
    """Update user role (admin only)."""
    user = user_crud.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot change your own role")
    
    valid_roles = ["admin", "recruiter", "hr", "viewer"]
    if payload.role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}")
    
    updated_user = user_crud.update(db, db_obj=user, obj_in={"role": payload.role})
    
    try:
        log_audit(
            db,
            user_id=str(current_user.id),
            action="update_user_role",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=request.client.host if request.client else None,
            details={"old_role": user.role, "new_role": payload.role},
        )
    except Exception as e:
        logger.warning("Audit log failed (update_user_role still succeeded): %s", e)
        db.rollback()
    
    return UserManagementRead.model_validate(updated_user)


@router.put("/users/{user_id}/activate", response_model=UserManagementRead)
def activate_user(
    user_id: str,
    request: Request,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> UserManagementRead:
    """Activate a user (admin only)."""
    user = user_crud.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = user_crud.update(db, db_obj=user, obj_in={"is_active": True})
    
    try:
        log_audit(
            db,
            user_id=str(current_user.id),
            action="activate_user",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=request.client.host if request.client else None,
        )
    except Exception as e:
        logger.warning("Audit log failed (activate_user still succeeded): %s", e)
        db.rollback()
    
    return UserManagementRead.model_validate(updated_user)


@router.put("/users/{user_id}/deactivate", response_model=UserManagementRead)
def deactivate_user(
    user_id: str,
    request: Request,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> UserManagementRead:
    """Deactivate a user (admin only)."""
    user = user_crud.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")
    
    updated_user = user_crud.update(db, db_obj=user, obj_in={"is_active": False})
    
    try:
        log_audit(
            db,
            user_id=str(current_user.id),
            action="deactivate_user",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=request.client.host if request.client else None,
        )
    except Exception as e:
        logger.warning("Audit log failed (deactivate_user still succeeded): %s", e)
        db.rollback()
    
    return UserManagementRead.model_validate(updated_user)
