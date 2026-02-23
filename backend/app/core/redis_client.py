"""Redis client for LLM cache and other shared state."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from redis import Redis

_redis_client: "Redis | None" = None


def get_redis_client() -> "Redis | None":
    """Return a Redis client for cache operations, or None if Redis is unavailable."""
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    try:
        from app.core.config import get_settings

        settings = get_settings()
        url = settings.REDIS_URL or settings.CELERY_BROKER_URL
        if not url:
            return None
        import redis

        _redis_client = redis.Redis.from_url(url, decode_responses=True)
        _redis_client.ping()
        return _redis_client
    except Exception:
        return None
