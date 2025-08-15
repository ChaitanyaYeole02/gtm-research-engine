from typing import List

from pydantic import BaseModel, Field


class Evidence(BaseModel):
    url: str
    title: str
    snippet: str
    source_name: str


class Findings(BaseModel):
    technologies: List[str] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)
    signals_found: int = 0


class CompanyResearchResult(BaseModel):
    domain: str
    confidence_score: float
    evidence_sources: int
    findings: Findings


class SearchPerformance(BaseModel):
    queries_per_second: float
    failed_requests: int


class BatchResearchResponse(BaseModel):
    research_id: str
    total_companies: int
    search_strategies_generated: int
    total_searches_executed: int
    processing_time_ms: int
    results: List[CompanyResearchResult]
    search_performance: SearchPerformance
