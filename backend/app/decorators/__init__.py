"""
Decorators package for the GTM Research Engine.

This package contains various decorators for API rate limiting, retry logic, and other cross-cutting concerns.
"""

from .api_rate_limiter import rate_limited

__all__ = [
    "rate_limited",
]
