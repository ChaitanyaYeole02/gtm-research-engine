"""Source integrations for web, news, jobs."""

from .base import BaseSource, SourceResult
from .google_search import GoogleSearchSource
from .news_search import NewsSearchSource

__all__ = [
    "BaseSource",
    "SourceResult", 
    "GoogleSearchSource",
    "NewsSearchSource",
]
