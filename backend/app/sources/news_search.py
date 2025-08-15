"""
News search source using NewsAPI.org for company intelligence.
Provides news articles, press releases, and announcements about companies.
"""

import asyncio
import os

from typing import List

from newsapi import NewsApiClient
from dotenv import load_dotenv

from app.decorators import rate_limited
from app.models.response import Evidence
from app.sources.base import BaseSource, SourceResult

from app.db import redis_client

# Load environment variables
load_dotenv()


class NewsSearchSource(BaseSource):
    """News search using NewsAPI.org for company intelligence."""
    
    channel_name = "news_search"

    PAGE_SIZE_MAPPING = {
        "quick": 2,
        "standard": 3, 
        "comprehensive": 5
    }

    def __init__(self):
        api_key = os.getenv("NEWS_API_KEY")
        if not api_key:
            raise ValueError("NEWS_API_KEY environment variable is required")
        
        self.client = NewsApiClient(api_key=api_key)

    @rate_limited("newsapi")
    async def fetch(
        self, domain: str, query: str, search_depth: str
    ) -> SourceResult:
        """Execute news search and return structured results."""
        try:
            # Extract company name from domain for better search
            company_name = domain.split('.')[0]

            # Build search query with company context
            search_query = f'"{company_name}" AND ({query})'
            
            # Execute search using NewsAPI client (in thread pool to avoid blocking event loop)
            data = await asyncio.to_thread(
                self.client.get_everything,
                q=search_query,
                sort_by="relevancy",
                language="en",
                page_size=self.PAGE_SIZE_MAPPING.get(search_depth, 3)
            )
            
            # Process results
            evidences = await self._process_news_results(data, domain)
            
            return SourceResult(
                channel=self.channel_name,
                domain=domain,
                query=query,
                evidences=evidences,
                ok=True
            )
            
        except Exception as e:
            return SourceResult(
                channel=self.channel_name,
                domain=domain,
                query=query,
                evidences=[],
                ok=False,
                error=f"NewsAPI search failed: {str(e)}"
            )
    
    async def _process_news_results(self, data: dict, domain: str) -> List[Evidence]:
        """Process NewsAPI response into Evidence objects."""
        evidences = []

        articles = data.get("articles", [])
        if not articles:
            return evidences
        
        for article in articles:
            # Skip articles with missing URLs
            if not article.get("url"):
                continue
            
            # Create evidence from article
            evidence = Evidence(
                url=article.get("url", ""),
                title=article.get("title", ""),
                snippet=article.get("description", ""),
                source_name=self.channel_name,
            )

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
        
        return evidences
