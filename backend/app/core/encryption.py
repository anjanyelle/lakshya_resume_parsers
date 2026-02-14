from __future__ import annotations

import json
from contextvars import ContextVar
from typing import Dict

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings

_current_tenant: ContextVar[str] = ContextVar("current_tenant", default="default")


def set_current_tenant(tenant_id: str) -> None:
    _current_tenant.set(tenant_id)


def get_current_tenant() -> str:
    return _current_tenant.get()


def _load_keys() -> Dict[str, str]:
    settings = get_settings()
    if settings.ENCRYPTION_KEYS_JSON:
        return json.loads(settings.ENCRYPTION_KEYS_JSON)
    if settings.ENCRYPTION_KEY:
        return {settings.DEFAULT_TENANT_ID: settings.ENCRYPTION_KEY}
    if settings.ENVIRONMENT.lower() in {"development", "local"}:
        return {}
    raise ValueError("Encryption key not configured")


def _get_key_for_tenant(tenant_id: str) -> bytes:
    keys = _load_keys()
    key = keys.get(tenant_id) or keys.get(get_settings().DEFAULT_TENANT_ID)
    if not key:
        if get_settings().ENVIRONMENT.lower() in {"development", "local"}:
            return b""
        raise ValueError("No encryption key for tenant")
    return key.encode("utf-8")


def encrypt_value(value: str) -> str:
    if get_settings().ENVIRONMENT.lower() in {"development", "local"}:
        return value
    key = _get_key_for_tenant(get_current_tenant())
    fernet = Fernet(key)
    token = fernet.encrypt(value.encode("utf-8"))
    return token.decode("utf-8")


def decrypt_value(token: str) -> str:
    if get_settings().ENVIRONMENT.lower() in {"development", "local"}:
        return token
    key = _get_key_for_tenant(get_current_tenant())
    fernet = Fernet(key)
    try:
        value = fernet.decrypt(token.encode("utf-8"))
    except InvalidToken as exc:
        raise ValueError("Invalid encryption token") from exc
    return value.decode("utf-8")
