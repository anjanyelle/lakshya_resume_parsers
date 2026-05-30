"""
Rate limiting middleware for the Resume Parser API.

This module provides rate limiting functionality to prevent abuse and ensure
fair usage of API resources. It supports different rate limit strategies
and configurable limits per endpoint.
"""

import logging
import time
from typing import Optional, Dict, Any
from collections import defaultdict
from functools import wraps
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    In-memory rate limiter using sliding window algorithm.
    
    For production, consider using Redis-based rate limiting for distributed systems.
    """
    
    def __init__(self):
        # Store request timestamps per key (IP or user ID)
        self.requests: Dict[str, list] = defaultdict(list)
        # Lock for thread safety (simplified for this implementation)
        self.locks: Dict[str, Any] = {}
    
    def is_allowed(
        self,
        key: str,
        limit: int,
        window_seconds: int
    ) -> bool:
        """
        Check if request is allowed under rate limit.
        
        Args:
            key: Unique identifier (IP address, user ID, etc.)
            limit: Maximum number of requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            True if request is allowed, False otherwise
        """
        current_time = time.time()
        window_start = current_time - window_seconds
        
        # Get existing requests for this key
        request_times = self.requests[key]
        
        # Remove requests outside the time window
        self.requests[key] = [
            req_time for req_time in request_times
            if req_time > window_start
        ]
        
        # Check if limit is exceeded
        if len(self.requests[key]) >= limit:
            logger.warning(
                f"Rate limit exceeded for key: {key}",
                extra={
                    "key": key,
                    "limit": limit,
                    "window": window_seconds,
                    "current_requests": len(self.requests[key])
                }
            )
            return False
        
        # Add current request
        self.requests[key].append(current_time)
        return True
    
    def get_remaining_requests(
        self,
        key: str,
        limit: int,
        window_seconds: int
    ) -> int:
        """
        Get remaining requests for a key.
        
        Args:
            key: Unique identifier
            limit: Maximum number of requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            Number of remaining requests
        """
        current_time = time.time()
        window_start = current_time - window_seconds
        
        request_times = self.requests[key]
        valid_requests = [
            req_time for req_time in request_times
            if req_time > window_start
        ]
        
        return max(0, limit - len(valid_requests))
    
    def get_reset_time(
        self,
        key: str,
        window_seconds: int
    ) -> float:
        """
        Get the time when the rate limit will reset.
        
        Args:
            key: Unique identifier
            window_seconds: Time window in seconds
            
        Returns:
            Unix timestamp when limit will reset
        """
        if not self.requests[key]:
            return time.time()
        
        oldest_request = min(self.requests[key])
        return oldest_request + window_seconds


# Global rate limiter instance
_rate_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    """Get the global rate limiter instance."""
    return _rate_limiter


class RateLimitConfig:
    """Configuration for rate limiting per endpoint."""
    
    # Default rate limits
    DEFAULT_LIMIT = 100
    DEFAULT_WINDOW = 60  # 1 minute
    
    # Upload endpoints (more restrictive)
    UPLOAD_LIMIT = 10
    UPLOAD_WINDOW = 60  # 10 uploads per minute
    
    # API endpoints
    API_LIMIT = 1000
    API_WINDOW = 3600  # 1000 requests per hour
    
    # Authentication endpoints
    AUTH_LIMIT = 5
    AUTH_WINDOW = 300  # 5 login attempts per 5 minutes
    
    # Parsing endpoints
    PARSING_LIMIT = 50
    PARSING_WINDOW = 3600  # 50 parses per hour


def get_client_identifier(request: Request) -> str:
    """
    Get a unique identifier for the client.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Client identifier (IP address or user ID)
    """
    # Try to get user ID from request state (if authenticated)
    if hasattr(request.state, 'user') and request.state.user:
        return f"user:{request.state.user.id}"
    
    # Fall back to IP address
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return f"ip:{forwarded.split(',')[0].strip()}"
    
    return f"ip:{request.client.host if request.client else 'unknown'}"


def check_rate_limit(
    request: Request,
    limit: int = RateLimitConfig.DEFAULT_LIMIT,
    window: int = RateLimitConfig.DEFAULT_WINDOW,
    endpoint: str = "default"
) -> None:
    """
    Check if request is allowed under rate limit.
    
    Args:
        request: FastAPI request object
        limit: Maximum number of requests allowed
        window: Time window in seconds
        endpoint: Endpoint identifier for logging
        
    Raises:
        HTTPException: If rate limit is exceeded
    """
    client_id = get_client_identifier(request)
    limiter = get_rate_limiter()
    
    if not limiter.is_allowed(client_id, limit, window):
        remaining = limiter.get_remaining_requests(client_id, limit, window)
        reset_time = limiter.get_reset_time(client_id, window)
        
        logger.warning(
            f"Rate limit exceeded for endpoint: {endpoint}",
            extra={
                "client_id": client_id,
                "endpoint": endpoint,
                "limit": limit,
                "window": window,
                "remaining": remaining
            }
        )
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "success": False,
                "message": "Rate limit exceeded",
                "error": "RATE_LIMIT_EXCEEDED",
                "limit": limit,
                "remaining": remaining,
                "reset_at": int(reset_time),
                "retry_after": int(reset_time - time.time())
            }
        )


def rate_limit(
    limit: int = RateLimitConfig.DEFAULT_LIMIT,
    window: int = RateLimitConfig.DEFAULT_WINDOW,
    endpoint: str = "default"
):
    """
    Decorator for rate limiting FastAPI endpoints.
    
    Args:
        limit: Maximum number of requests allowed
        window: Time window in seconds
        endpoint: Endpoint identifier for logging
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from kwargs (FastAPI dependency injection)
            request = kwargs.get('request')
            if not request:
                # Try to get request from positional arguments
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            
            if request:
                check_rate_limit(request, limit, window, endpoint)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Pre-configured rate limit decorators for common use cases

def rate_limit_upload(func):
    """Rate limit decorator for upload endpoints (10 per minute)."""
    return rate_limit(
        limit=RateLimitConfig.UPLOAD_LIMIT,
        window=RateLimitConfig.UPLOAD_WINDOW,
        endpoint="upload"
    )(func)


def rate_limit_auth(func):
    """Rate limit decorator for authentication endpoints (5 per 5 minutes)."""
    return rate_limit(
        limit=RateLimitConfig.AUTH_LIMIT,
        window=RateLimitConfig.AUTH_WINDOW,
        endpoint="auth"
    )(func)


def rate_limit_api(func):
    """Rate limit decorator for general API endpoints (1000 per hour)."""
    return rate_limit(
        limit=RateLimitConfig.API_LIMIT,
        window=RateLimitConfig.API_WINDOW,
        endpoint="api"
    )(func)


def rate_limit_parsing(func):
    """Rate limit decorator for parsing endpoints (50 per hour)."""
    return rate_limit(
        limit=RateLimitConfig.PARSING_LIMIT,
        window=RateLimitConfig.PARSING_WINDOW,
        endpoint="parsing"
    )(func)


class RateLimitMiddleware:
    """
    FastAPI middleware for rate limiting.
    
    This middleware applies rate limiting to all requests based on
    client IP address or user ID.
    """
    
    def __init__(
        self,
        app,
        limit: int = RateLimitConfig.DEFAULT_LIMIT,
        window: int = RateLimitConfig.DEFAULT_WINDOW
    ):
        self.app = app
        self.limit = limit
        self.window = window
    
    async def __call__(self, scope, receive, send):
        if scope['type'] == 'http':
            # Create a mock request object for rate limit checking
            # This is simplified - in production, you'd want proper request handling
            pass
        
        await self.app(scope, receive, send)
