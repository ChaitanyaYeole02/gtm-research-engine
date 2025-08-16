import asyncio
import httpx
import re

from typing import Any, Dict, List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models.response import Evidence
from app.sources.base import BaseSource, SourceResult


class JobsSearchSource(BaseSource):
    """Jobs search using Greenhouse API with TF-IDF matching."""

    channel_name = "jobs_search"

    def __init__(self):
        self._tfidf_vectorizer = None
        
    def _get_tfidf_model(self):
        """Get or initialize the TF-IDF vectorizer."""
        if self._tfidf_vectorizer is None:
            self._tfidf_vectorizer = TfidfVectorizer(
                max_features=2000,           # More features for richer content
                stop_words='english',
                ngram_range=(1, 3),          # Include trigrams for better phrase matching
                lowercase=True,
                min_df=1,                    # Include rare terms (good for specialized roles)
                max_df=0.95,                 # Remove very common terms
                token_pattern=r'\b[a-zA-Z]+\b'  # Only alphabetic tokens
            )
            
        return self._tfidf_vectorizer

    async def _search_jobs_tfidf(self, jobs: List[Dict], query: str, threshold: float = 0.1) -> List[Tuple[Dict, float]]:
        """
        TF-IDF based job search with similarity scoring.
        Uses asyncio.to_thread for CPU-intensive operations to avoid blocking event loop.
        """
        if not jobs:
            return []

        def _compute_similarities():
            """CPU-intensive TF-IDF computation."""
            vectorizer = self._get_tfidf_model()
            if vectorizer is None:
                return []

            # Prepare job texts (title + content)
            job_texts = []
            for job in jobs:
                title = job.get('title', '')
                content = job.get('content', '')
                
                # Clean HTML tags from content if present
                content_clean = re.sub(r'<[^>]+>', ' ', content) if content else ''
                
                # Combine title and content (weight title higher by repeating it)
                combined_text = f"{title} {title} {content_clean}".strip()
                job_texts.append(combined_text)
            
            # Add search term to fit the vectorizer
            all_texts = job_texts + [query]
            
            # Generate TF-IDF vectors
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            search_vector = tfidf_matrix[-1]  # Last item is search term
            job_vectors = tfidf_matrix[:-1]   # All except last
            
            # Calculate similarities
            similarities = cosine_similarity(search_vector, job_vectors)[0]
            
            # Filter and collect matches
            matches = []
            for job, similarity in zip(jobs, similarities):
                if similarity >= threshold:
                    matches.append((job, float(similarity)))
            
            # Sort by similarity score (descending)
            return sorted(matches, key=lambda x: x[1], reverse=True)

        # Run CPU-intensive work in thread pool to avoid blocking event loop
        return await asyncio.to_thread(_compute_similarities)

    async def _process_jobs(self, data: Dict[str, Any], query: str) -> List[Evidence]:
        """Process jobs data and filter using TF-IDF search."""
        jobs = data.get("jobs", [])

        if not jobs:
            return []
        
        filtered_jobs = await self._search_jobs_tfidf(jobs, query, threshold=0.05)
        
        # Convert to Evidence objects
        evidences = []
        for job, similarity_score in filtered_jobs[:10]:  # Limit to top 10 matches
            title = job.get('title', 'Unknown Job')
            location = job.get('location', {}).get('name', 'Unknown Location')
            job_url = job.get('absolute_url', '')
            updated_at = job.get('updated_at', '')
            
            # Create evidence text with job details
            evidence_text = f"Job Opening: {title} at {location}"
            if updated_at:
                evidence_text += f" (Updated: {updated_at})"
            
            evidence = Evidence(
                url=job_url,
                title=title,
                snippet=evidence_text,
                source_name=self.channel_name,
            )
            evidences.append(evidence)
        
        return evidences

    async def fetch(
        self, domain: str, query: str, search_depth: str
    ) -> SourceResult:
        try:
            company_name = domain.split('.')[0]

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://boards-api.greenhouse.io/v1/boards/{company_name}/jobs?content=true"
                )

                if response.status_code != 200:
                    return SourceResult(
                        channel=self.channel_name,
                        domain=domain,
                        query=query,
                        evidences=[],
                        ok=False,
                        error=f"Failed to fetch jobs: {response.status_code}"
                    )

                jobs_data = response.json()
                
                evidences = await self._process_jobs(jobs_data, query)

                return SourceResult(
                    channel=self.channel_name,
                    domain=domain,
                    query=query,
                    evidences=evidences,
                    ok=True,
                )
        except Exception as e:
            return SourceResult(
                channel=self.channel_name,
                domain=domain,
                query=query,
                evidences=[],
                ok=False,
                error=str(e)
            )
            