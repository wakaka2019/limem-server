"""
Rate limiting middleware for PowerMem API
"""

from fastapi import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from ..config import config
from ..models.errors import ErrorCode

# Limiter is created lazily to avoid spawning a background timer thread
# on import in restricted Docker containers (can't start new thread).
_limiter = None


def _get_limiter() -> Limiter:
    global _limiter
    if _limiter is None:
        _limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")
    return _limiter


def rate_limit_middleware(app):
    """
    Setup rate limiting middleware for FastAPI app.
    """
    if not config.rate_limit_enabled:
        return

    app.state.limiter = _get_limiter()
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


def get_rate_limit_string() -> str:
    """
    Get rate limit string from config.

    Returns:
        Rate limit string (e.g., "100/minute")
    """
    return f"{config.rate_limit_per_minute}/minute"
