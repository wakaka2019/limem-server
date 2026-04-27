"""
Rate limiting middleware for PowerMem API
"""

from fastapi import Request
from slowapi.errors import RateLimitExceeded
from ..config import config


class _NoOpLimiter:
    """Drop-in stub for slowapi.Limiter when thread creation is restricted."""

    def limit(self, *args, **kwargs):
        def decorator(func):
            return func
        return decorator

    def __getattr__(self, name):
        return lambda *a, **kw: None


# Always available for import by api/v1/memories.py etc.
# Uses no-op stub so no background timer thread is spawned.
limiter = _NoOpLimiter()


def rate_limit_middleware(app):
    """
    Setup rate limiting middleware for FastAPI app.
    """
    if not config.rate_limit_enabled:
        return

    # Only import and create real Limiter when rate limiting is explicitly enabled.
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    real_limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")
    app.state.limiter = real_limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


def get_rate_limit_string() -> str:
    """
    Get rate limit string from config.

    Returns:
        Rate limit string (e.g., "100/minute")
    """
    return f"{config.rate_limit_per_minute}/minute"
