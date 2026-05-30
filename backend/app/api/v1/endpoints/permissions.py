from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import enforce_rate_limit_request, get_current_user, get_db, require_role
from app.models import Permission, RolePermission, User
from app.schemas.permission import (
    PermissionListResponse,
    PermissionRead,
    RolePermissionRead,
    RolePermissionUpdate,
    RolesResponse,
)
from app.utils.audit import log_audit

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/permissions", response_model=PermissionListResponse)
def list_permissions(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    module: Optional[str] = Query(default=None),
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> PermissionListResponse:
    """List all permissions (admin only)."""
    query = db.query(Permission)
    if module:
        query = query.filter(Permission.module == module)
    
    permissions = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return PermissionListResponse(
        permissions=[PermissionRead.model_validate(p) for p in permissions],
        total=total,
    )


@router.get("/roles", response_model=RolesResponse)
def list_roles(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> RolesResponse:
    """List all roles (admin only)."""
    roles = db.query(RolePermission.role).distinct().all()
    return RolesResponse(roles=[r[0] for r in roles])


@router.get("/roles/{role}/permissions", response_model=RolePermissionRead)
def get_role_permissions(
    role: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> RolePermissionRead:
    """Get permissions for a specific role (admin only)."""
    valid_roles = ["admin", "recruiter", "hr", "viewer"]
    if role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}")
    
    role_permissions = (
        db.query(Permission)
        .join(RolePermission)
        .filter(RolePermission.role == role)
        .all()
    )
    
    return RolePermissionRead(
        role=role,
        permissions=[PermissionRead.model_validate(p) for p in role_permissions],
    )


@router.put("/roles/{role}/permissions", response_model=RolePermissionRead)
def update_role_permissions(
    role: str,
    payload: RolePermissionUpdate,
    request: Request,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> RolePermissionRead:
    """Update permissions for a specific role (admin only)."""
    enforce_rate_limit_request(request, limit=10, per_seconds=60)
    
    valid_roles = ["admin", "recruiter", "hr", "viewer"]
    if role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}")
    
    # Prevent modifying admin permissions (admin always has all permissions)
    if role == "admin":
        raise HTTPException(status_code=400, detail="Cannot modify admin permissions")
    
    # Validate that all permission names exist
    existing_permissions = db.query(Permission.name).all()
    existing_permission_names = {p[0] for p in existing_permissions}
    
    for perm_name in payload.permissions:
        if perm_name not in existing_permission_names:
            raise HTTPException(status_code=400, detail=f"Invalid permission: {perm_name}")
    
    # Delete existing role permissions
    db.query(RolePermission).filter(RolePermission.role == role).delete()
    
    # Add new role permissions
    for perm_name in payload.permissions:
        permission = db.query(Permission).filter(Permission.name == perm_name).first()
        if permission:
            db.add(RolePermission(role=role, permission_id=permission.id))
    
    db.commit()
    
    try:
        log_audit(
            db,
            user_id=str(current_user.id),
            action="update_role_permissions",
            resource_type="role",
            resource_id=role,
            ip_address=request.client.host if request.client else None,
            details={"permissions": payload.permissions},
        )
    except Exception as e:
        logger.warning("Audit log failed (update_role_permissions still succeeded): %s", e)
        db.rollback()
    
    # Return updated role permissions
    role_permissions = (
        db.query(Permission)
        .join(RolePermission)
        .filter(RolePermission.role == role)
        .all()
    )
    
    return RolePermissionRead(
        role=role,
        permissions=[PermissionRead.model_validate(p) for p in role_permissions],
    )
