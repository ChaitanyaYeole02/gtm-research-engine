import asyncio
import os

from typing import List

from dotenv import load_dotenv
from tavily import TavilyClient

from app.decorators import rate_limited
from app.models.response import Evidence
from app.sources.base import BaseSource, SourceResult

from app.db import redis_client

# Load environment variables
load_dotenv()


class GoogleSearchSource(BaseSource):
    """Real Google Search using Tavily Search API."""
    
    channel_name = "google_search"
    
    # Map our search depth values to Tavily's expected values
    SEARCH_DEPTH_MAPPING = {
        "quick": "basic",
        "standard": "advanced", 
        "comprehensive": "advanced"
    }

    MAX_RESULTS_MAPPING = {
        "quick": 2,
        "standard": 3, 
        "comprehensive": 5
    }

    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY environment variable is required")
        
        self.client = TavilyClient(api_key=api_key)

    @rate_limited("tavily")
    async def fetch(
        self, domain: str, query: str, search_depth: str
    ) -> SourceResult:
        """Execute search query using Tavily and return structured results."""
        try:
            # Execute search with Tavily (in thread pool to avoid blocking event loop)
            response = await asyncio.to_thread(
                self.client.search,
                query=query,
                search_depth=self.SEARCH_DEPTH_MAPPING.get(search_depth, "basic"),
                max_results=self.MAX_RESULTS_MAPPING.get(search_depth, 2),
            )
            
            evidences: List[Evidence] = []
            
            # Process search results
            if response["results"]:
                for result in response["results"]:
                    evidence = Evidence(
                        url=result.get("url", ""),
                        title=result.get("title", "No title")[:200],  # Limit title length
                        snippet=result.get("content", "")[:500],  # Limit snippet length
                        source_name=self.channel_name,
                    )

                    # Check cache asynchronously to avoid blocking event loop
                    is_cached = await asyncio.to_thread(
                        redis_client.is_evidence_cached, domain, evidence
                    )
                    if is_cached:
                        continue
            
                    # Add to cache asynchronously
                    await asyncio.to_thread(
                        redis_client.add_evidence_to_cache, domain, evidence
                    )

                    evidences.append(evidence)
            
            # Return successful result even if no evidences (empty results are valid)
            return SourceResult(
                channel=self.channel_name,
                domain=domain,
                query=query,
                evidences=evidences,
                ok=True
            )
            
        except Exception as e:
            # Return error result
            return SourceResult(
                channel=self.channel_name,
                domain=domain,
                query=query,
                evidences=[],
                ok=False,
                error=f"Tavily search failed: {str(e)}"
            )
