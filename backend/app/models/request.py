from typing import List, Literal

from pydantic import BaseModel, Field


class BatchResearchRequest(BaseModel):
    research_goal: str = Field(..., description="The high-level research objective")
    company_domains: List[str] = Field(..., description="Company domains to analyze")
    search_depth: Literal["quick", "standard", "comprehensive"] = Field(
        ..., 
        description="Controls the number of strategies and search breadth",
    )
    max_parallel_searches: int = Field(
        ..., description="Overrides default global concurrency if provided"
    )
    confidence_threshold: float = Field(
        ...,
        ge=0.0, 
        le=1.0, 
        description="Threshold to include a finding in results"
    )
