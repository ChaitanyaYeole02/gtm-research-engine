"""API package containing FastAPI routers and endpoints."""

from .routes import router as api_router  # noqa: F401

__all__ = ["api_router"]
