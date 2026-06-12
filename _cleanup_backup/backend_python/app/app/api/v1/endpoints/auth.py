from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from jose import JWTError
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session

import secrets

from app.api.deps import enforce_rate_limit_request, get_current_user, get_db, require_role
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.crud.user import user as user_crud
from app.models import ApiKey
from app.models.revoked_token import RevokedToken
from app.schemas.api_key import ApiKeyCreate, ApiKeyRead, ApiKeyResponse
from app.utils.audit import log_audit
from app.schemas.auth import RefreshRequest, TokenResponse, UserCreate, UserRead

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/auth/register", response_model=UserRead)
def register(
    payload: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> UserRead:
    enforce_rate_limit_request(request, limit=5, per_seconds=60)
    existing = user_crud.get_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = user_crud.create(
        db,
        {
            "email": payload.email,
            "hashed_password": get_password_hash(payload.password),
            "is_active": True,
            "role": payload.role or "recruiter",
        },
    )
    try:
        log_audit(
            db,
            user_id=str(user.id),
            action="register",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=request.client.host if request.client else None,
        )
    except Exception as e:
        logger.warning("Audit log failed (register still succeeded): %s", e)
        db.rollback()  # clear failed audit so session is usable for response
    return UserRead.model_validate(user)


@router.post("/auth/login", response_model=TokenResponse)
def login(
    payload: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> TokenResponse:
    enforce_rate_limit_request(request, limit=10, per_seconds=60)
    user = user_crud.get_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(subject=user.email)
    refresh_token = create_refresh_token(subject=user.email)
    try:
        log_audit(
            db,
            user_id=str(user.id),
            action="login",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=request.client.host if request.client else None,
        )
    except Exception as e:
        logger.warning("Audit log failed (login still succeeded): %s", e)
        db.rollback()
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/auth/refresh", response_model=TokenResponse)
def refresh(
    payload: RefreshRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> TokenResponse:
    enforce_rate_limit_request(request, limit=10, per_seconds=60)
    try:
        decoded = decode_token(payload.refresh_token)
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    if decoded.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token")

    jti = decoded.get("jti")
    subject = decoded.get("sub")
    if not jti or not subject:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        revoked = db.query(RevokedToken).filter(RevokedToken.jti == jti).first()
        if revoked:
            raise HTTPException(status_code=401, detail="Token revoked")
    except ProgrammingError as e:
        err_msg = str(getattr(e, "orig", e) or e).lower()
        if "revoked_tokens" in err_msg:
            db.rollback()
        else:
            raise

    access_token = create_access_token(subject=subject)
    refresh_token = create_refresh_token(subject=subject)
    user = user_crud.get_by_email(db, subject)
    try:
        log_audit(
            db,
            user_id=str(user.id) if user else None,
            action="refresh",
            resource_type="user",
            resource_id=str(user.id) if user else None,
            ip_address=request.client.host if request.client else None,
        )
    except Exception as e:
        logger.warning("Audit log failed (refresh still succeeded): %s", e)
        db.rollback()
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/auth/logout")
def logout(
    request: Request,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    enforce_rate_limit_request(request, limit=10, per_seconds=60)
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "").strip()
    if not token:
        raise HTTPException(status_code=400, detail="Missing token")

    try:
        decoded = decode_token(token)
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    jti = decoded.get("jti")
    exp = decoded.get("exp")
    subject = decoded.get("sub")
    if not jti or not subject or not exp:
        raise HTTPException(status_code=401, detail="Invalid token")

    expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
    db.add(
        RevokedToken(jti=jti, subject=subject, expires_at=expires_at)
    )
    db.commit()
    try:
        log_audit(
            db,
            user_id=str(current_user.id),
            action="logout",
            resource_type="user",
            resource_id=str(current_user.id),
            ip_address=request.client.host if request.client else None,
        )
    except Exception as e:
        logger.warning("Audit log failed (logout still succeeded): %s", e)
        db.rollback()
    logger.info("User logged out", extra={"user": current_user.email})
    return {"status": "ok"}


@router.post("/auth/api-keys", response_model=ApiKeyResponse)
def create_api_key(
    payload: ApiKeyCreate,
    request: Request,
    current_user=Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> ApiKeyResponse:
    enforce_rate_limit_request(request, limit=10, per_seconds=60)
    raw_key = secrets.token_urlsafe(32)
    import hashlib

    key_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
    api_key = ApiKey(
        key_hash=key_hash,
        role=payload.role,
        subject=payload.subject,
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    try:
        log_audit(
            db,
            user_id=str(current_user.id),
            action="create_api_key",
            resource_type="api_key",
            resource_id=str(api_key.id),
            ip_address=request.client.host if request.client else None,
        )
    except Exception as e:
        logger.warning("Audit log failed (create_api_key still succeeded): %s", e)
        db.rollback()
    return ApiKeyResponse(api_key=raw_key, key_id=api_key.id)


@router.delete("/auth/api-keys/{key_id}", response_model=ApiKeyRead)
def revoke_api_key(
    key_id: str,
    request: Request,
    current_user=Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> ApiKeyRead:
    enforce_rate_limit_request(request, limit=10, per_seconds=60)
    api_key = db.get(ApiKey, key_id)
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    api_key.revoked_at = datetime.now(timezone.utc)
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    try:
        log_audit(
            db,
            user_id=str(current_user.id),
            action="revoke_api_key",
            resource_type="api_key",
            resource_id=str(api_key.id),
            ip_address=request.client.host if request.client else None,
        )
    except Exception as e:
        logger.warning("Audit log failed (revoke_api_key still succeeded): %s", e)
        db.rollback()
    return ApiKeyRead.model_validate(api_key)
