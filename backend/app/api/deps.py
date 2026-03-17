from __future__ import annotations

import time
from typing import Generator

from fastapi import Depends, HTTPException, Request, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
import redis
import structlog
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.encryption import set_current_tenant
from app.core.security import decode_token
from app.models import ApiKey, RevokedToken, User
from app.core.database import get_db

__all__ = [
    "get_db",
    "Session",
    "Generator",
    "get_current_subject",
    "get_current_user",
    "enforce_rate_limit",
    "require_role",
]

_auth_scheme = HTTPBearer(auto_error=False)
_rate_limit_cache: dict[str, list[float]] = {}
_redis_client: redis.Redis | None = None


def get_current_subject(
    credentials: HTTPAuthorizationCredentials | None = Depends(_auth_scheme),
) -> str:
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing token")
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    subject = payload.get("sub")
    token_type = payload.get("type")
    if not subject or token_type != "access":
        raise HTTPException(status_code=401, detail="Invalid token")
    return str(subject)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_auth_scheme),
    db: Session = Depends(get_db),
    api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> User:
    if api_key:
        key_hash = _hash_api_key(api_key)
        key = db.query(ApiKey).filter(ApiKey.key_hash == key_hash).first()
        if not key or key.revoked_at:
            raise HTTPException(status_code=401, detail="Invalid API key")
        user = db.query(User).filter(User.email == key.subject).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        user.role = key.role
        set_current_tenant(user.tenant_id)
        structlog.contextvars.bind_contextvars(user_id=str(user.id))
        _set_sentry_user(user)
        return user

    if not credentials:
        raise HTTPException(status_code=401, detail="Missing token")
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    subject = payload.get("sub")
    jti = payload.get("jti")
    token_type = payload.get("type")
    if not subject or token_type != "access":
        raise HTTPException(status_code=401, detail="Invalid token")
    if jti:
        try:
            revoked = db.query(RevokedToken).filter(RevokedToken.jti == jti).first()
            if revoked:
                raise HTTPException(status_code=401, detail="Token revoked")
        except ProgrammingError as e:
            err_msg = str(getattr(e, "orig", e) or e).lower()
            if "revoked_tokens" in err_msg:
                db.rollback()  # Reset transaction so subsequent queries (e.g. User) can run
            else:
                raise
    user = db.query(User).filter(User.email == subject).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    set_current_tenant(user.tenant_id)
    structlog.contextvars.bind_contextvars(user_id=str(user.id))
    _set_sentry_user(user)
    return user


def _set_sentry_user(user: User) -> None:
    try:
        import sentry_sdk

        sentry_sdk.set_user({"id": str(user.id), "email": user.email})
    except Exception:
        return


def enforce_rate_limit(
    key: str, limit: int = 10, per_seconds: int = 60
) -> None:
    settings = get_settings()
    if settings.ENVIRONMENT.lower() in {"development", "local"}:
        return
    if settings.REDIS_URL:
        global _redis_client
        if _redis_client is None:
            _redis_client = redis.Redis.from_url(settings.REDIS_URL)
        bucket = int(time.time() // per_seconds)
        redis_key = f"rate:{key}:{bucket}"
        count = _redis_client.incr(redis_key)
        if count == 1:
            _redis_client.expire(redis_key, per_seconds)
        if count > limit:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Try again later.",
                headers={"Retry-After": str(per_seconds)},
            )
        return

    now = time.time()
    window_start = now - per_seconds
    timestamps = _rate_limit_cache.get(key, [])
    timestamps = [ts for ts in timestamps if ts >= window_start]
    if len(timestamps) >= limit:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later.",
            headers={"Retry-After": str(per_seconds)},
        )
    timestamps.append(now)
    _rate_limit_cache[key] = timestamps


def enforce_rate_limit_request(
    request: Request,
    limit: int = 10,
    per_seconds: int = 60,
) -> None:
    key = request.client.host if request.client else "anonymous"
    enforce_rate_limit(key, limit=limit, per_seconds=per_seconds)


def require_role(*roles: str):
    def _checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user

    return _checker


def _hash_api_key(value: str) -> str:
    import hashlib

    return hashlib.sha256(value.encode("utf-8")).hexdigest()
