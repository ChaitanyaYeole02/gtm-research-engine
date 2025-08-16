"""Source integrations for web, news, jobs."""

from .base import BaseSource, SourceResult
from .google_search import GoogleSearchSource
from .jobs_search import JobsSearchSource
from .news_search import NewsSearchSource

__all__ = [
    "BaseSource",
    "SourceResult", 
    "GoogleSearchSource",
    "JobsSearchSource",
    "NewsSearchSource",
]
