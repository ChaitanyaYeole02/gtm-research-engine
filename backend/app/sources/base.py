from dataclasses import dataclass
from typing import List, Optional

from app.models.response import Evidence


@dataclass
class SourceResult:
    channel: str
    domain: str
    query: str
    evidences: List[Evidence]
    ok: bool
    error: Optional[str] = None


class BaseSource:
    channel_name: str

    async def fetch(
        self, domain: str, query: str, search_depth: str
    ) -> SourceResult:
        raise NotImplementedError
