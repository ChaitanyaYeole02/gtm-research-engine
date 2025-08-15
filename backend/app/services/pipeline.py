import asyncio
import time

from collections import defaultdict
from typing import AsyncGenerator, Dict, List, Tuple

import orjson

from app.db import redis_client

from app.core import CircuitBreaker, RunMetrics, get_settings
from app.models import CompanyResearchResult, Evidence, Findings, QueryStrategy
from app.services import EnhancedStreamingAggregator, Extractor
from app.sources import (
    BaseSource, GoogleSearchSource, NewsSearchSource, SourceResult
)



class ResearchPipeline:
    def __init__(
        self,
        run_id: str,
        research_goal: str,
        search_depth: str,
        company_domains: List[str],
        strategies: List[QueryStrategy],
        max_parallel_searches: int,
        confidence_threshold: float,
        metrics: RunMetrics,
    ) -> None:
        settings = get_settings()

        self.run_id = run_id
        self.research_goal = research_goal
        self.search_depth = search_depth
        self.company_domains = company_domains
        self.strategies = strategies
        self.max_parallel_searches = max_parallel_searches
        self.confidence_threshold = confidence_threshold
        self.metrics = metrics

        # Source Pools for rate limiting
        self.source_pools: Dict[str, asyncio.Semaphore] = {
            "google_search": asyncio.Semaphore(max_parallel_searches),   
            "news_search": asyncio.Semaphore(max_parallel_searches),
        }
        self.default_pool = asyncio.Semaphore(max(max_parallel_searches // 4, 2))

        # Sources
        self.sources: Dict[str, BaseSource] = {
            "google_search": GoogleSearchSource(),
            "news_search": NewsSearchSource(),
        }
        
        self.signal_extractor = Extractor()
        self.breakers: Dict[str, CircuitBreaker] = {
            channel: CircuitBreaker(
                failure_threshold=settings.circuit_breaker_failures,
                reset_timeout_seconds=settings.circuit_breaker_reset_seconds,
            )
            for channel in self.sources.keys()
        }
        
    async def _execute_one(
        self, domain: str, strategy: QueryStrategy, search_depth: str
    ) -> Tuple[str, SourceResult]:
        query = strategy.build_query(domain)

        source = self.sources.get(strategy.channel)
        if source is None:
            return domain, SourceResult(
                channel=strategy.channel,
                domain=domain,
                query=query,
                evidences=[],
                ok=False,
                error="unknown channel"
            )

        breaker = self.breakers[strategy.channel]
        if not breaker.allow_request():
            return domain, SourceResult(
                channel=strategy.channel,
                domain=domain,
                query=query,
                evidences=[],
                ok=False,
                error="circuit open"
            )

        source_pool = self.source_pools.get(strategy.channel, self.default_pool)
        pool_name = strategy.channel if strategy.channel in self.source_pools else "default_pool"
        
        async with source_pool:
            try:
                result = await source.fetch(
                    domain=domain, query=query, search_depth=search_depth
                )
                
                if result.ok and result.evidences:
                    self.metrics.record_query(1)    
                    breaker.record_success()
                else:
                    self.metrics.record_failure(1)
                    breaker.record_failure()

                return domain, result
            except Exception as exc:
                self.metrics.record_failure(1)
                breaker.record_failure()

                return domain, SourceResult(
                    channel=strategy.channel,
                    domain=domain,
                    query=query,
                    evidences=[],
                    ok=False,
                    error=str(exc)
                )

    async def analyze_domain(self, domain: str, evidences: List[Evidence]):
        await asyncio.to_thread(redis_client.clear_cache, domain)
        
        if evidences:
            analysis_result = await self.signal_extractor.analyze_company(
                self.research_goal, evidences
            )
            return self._build_company_result(domain, evidences, analysis_result)
        else:
            return self._build_empty_result(domain)
        

    async def run(self) -> Tuple[List[CompanyResearchResult], int]: 
        """
        Execute research pipeline with batch LLM analysis.
        
        Flow:
        1. Collect ALL evidence from ALL sources for ALL domains
        2. For each domain, perform single LLM analysis on all evidence
        3. Build final results with confidence scores and findings
        """
        tasks: List[asyncio.Task[Tuple[str, SourceResult]]] = []
        for domain in self.company_domains:
            for strategy in self.strategies:
                tasks.append(
                    asyncio.create_task(
                        self._execute_one(domain, strategy, self.search_depth)
                    )
                )

        total_planned = len(tasks)   
        domain_to_evidence: Dict[str, List[Evidence]] = defaultdict(list)
        completed_count = 0
        
        for coro in asyncio.as_completed(tasks):
            domain, res = await coro
            completed_count += 1
            
            if res.ok and res.evidences:
                domain_to_evidence[domain].extend(res.evidences)

        # Step 2: Batch LLM analysis for each domain
        domain_tasks = [
            asyncio.create_task(self.analyze_domain(domain, evidences))
            for domain, evidences in domain_to_evidence.items()
        ]
        results: List[CompanyResearchResult] = []
        for coro in asyncio.as_completed(domain_tasks):
            result = await coro
            results.append(result)

        # Include domains with no evidence at all
        missing_domains = set(self.company_domains) - set(domain_to_evidence.keys())
        for domain in missing_domains:
            result = self._build_empty_result(domain)
            results.append(result)
        
        return results, total_planned
    
    def _build_company_result(self, domain: str, evidences: List[Evidence], analysis_result: Dict) -> CompanyResearchResult:
        """Build CompanyResearchResult from LLM analysis."""
        
        # Extract technologies, signals, and confidence from LLM analysis
        technologies = analysis_result.get("technologies", [])
        goal_match_signals = analysis_result.get("goal_match_signals", [])
        confidence_score = analysis_result.get("confidence_score", 0.0)
        
        # Calculate evidence sources count
        evidence_sources = len(set(evidence.source_name for evidence in evidences))
        
        # Build findings with LLM results
        findings = Findings(
            technologies=technologies,           # Store extracted technologies (TensorFlow, Python, etc.)
            evidence=evidences,
            signals_found=len(goal_match_signals)  # Count of signals indicating goal match
        )
        
        return CompanyResearchResult(
            domain=domain,
            confidence_score=round(confidence_score, 2),
            evidence_sources=evidence_sources,
            findings=findings
        )
    
    def _build_empty_result(self, domain: str) -> CompanyResearchResult:
        """Build empty result for domains with no evidence."""        
        findings = Findings(
            technologies=[],
            evidence=[],
            signals_found=0
        )
        
        return CompanyResearchResult(
            domain=domain,
            confidence_score=0.0,
            evidence_sources=0,
            findings=findings
        )
    
    async def run_stream_optimized(self) -> AsyncGenerator[str, None]:
        """
        Optimized streaming pipeline with async domain processing and reduced event frequency.
        
        Key improvements:
        - Async domain processing for better parallelization  
        - Reduced event noise (fewer, more meaningful events)
        - Better performance through batching
        - Cleaner error handling
        """
        
        # Step 1: Evidence Collection (parallel)
        yield orjson.dumps({
            "type": "pipeline_start",
            "message": "Starting evidence collection",
            "domains": self.company_domains,
            "total_strategies": len(self.strategies),
            "timestamp": time.time()
        }).decode()
        
        # Create all tasks for evidence collection
        tasks: List[asyncio.Task[Tuple[str, SourceResult]]] = []
        for domain in self.company_domains:
            for strategy in self.strategies:
                tasks.append(
                    asyncio.create_task(
                        self._execute_one(domain, strategy, self.search_depth)
                    )
                )

        total_planned = len(tasks)
        domain_to_evidence: Dict[str, List[Evidence]] = defaultdict(list)
        completed_count = 0
        progress_updates = [25, 50, 75, 100]  # Send updates at these percentages
        
        # Process evidence collection with progress updates
        for coro in asyncio.as_completed(tasks):
            domain, res = await coro
            completed_count += 1
            
            if res.ok and res.evidences:
                domain_to_evidence[domain].extend(res.evidences)
            
            # Send progress updates at key milestones
            progress_percent = int((completed_count / total_planned) * 100)
            if progress_percent in progress_updates:
                progress_updates.remove(progress_percent)
                
                yield orjson.dumps({
                    "type": "evidence_progress",
                    "progress": progress_percent,
                    "completed": completed_count,
                    "total": total_planned,
                    "domains_with_evidence": len(domain_to_evidence),
                    "timestamp": time.time()
                }).decode()
        
        # Evidence collection complete
        yield orjson.dumps({
            "type": "evidence_complete",
            "message": "Evidence collection finished",
            "total_evidence": sum(len(evidences) for evidences in domain_to_evidence.values()),
            "domains_with_evidence": len(domain_to_evidence),
            "timestamp": time.time()
        }).decode()
        
        # Step 2: Async Domain Analysis (parallel LLM processing!)
        yield orjson.dumps({
            "type": "analysis_start", 
            "message": "Starting domain analysis",
            "domains_to_analyze": len(domain_to_evidence),
            "timestamp": time.time()
        }).decode()
        
        async def analyze_domain_async(domain: str, evidences: List[Evidence]) -> CompanyResearchResult:
            """Analyze a single domain asynchronously."""
            # Clear cache
            await asyncio.to_thread(redis_client.clear_cache, domain)
            
            if evidences:
                # LLM analysis
                analysis_result = await self.signal_extractor.analyze_company(
                    self.research_goal, evidences
                )
                return self._build_company_result(domain, evidences, analysis_result)
            else:
                return self._build_empty_result(domain)
        
        # Create analysis tasks for all domains (PARALLEL!)
        async def analyze_with_domain(domain: str, evidences: List[Evidence]) -> Tuple[str, CompanyResearchResult]:
            """Wrapper to return domain with result."""
            result = await analyze_domain_async(domain, evidences)
            return domain, result
        
        analysis_tasks = []
        for domain, evidences in domain_to_evidence.items():
            task = asyncio.create_task(analyze_with_domain(domain, evidences))
            analysis_tasks.append(task)
        
        # Process domain analysis results as they complete
        results: List[CompanyResearchResult] = []
        domains_analyzed = 0
        total_domains = len(analysis_tasks)
        
        for task_coro in asyncio.as_completed(analysis_tasks):
            domain, result = await task_coro
            results.append(result)
            domains_analyzed += 1
            
            # Send domain completion event
            yield orjson.dumps({
                "type": "domain_analyzed",
                "domain": domain,
                "confidence": result.confidence_score,
                "evidence_count": len(result.findings.evidence) if result.findings else 0,
                "technologies": result.findings.technologies if result.findings else [],
                "progress": domains_analyzed,
                "total": total_domains,
                "timestamp": time.time()
            }).decode()
        
        # Add missing domains (no evidence found)
        missing_domains = set(self.company_domains) - set(domain_to_evidence.keys())
        for domain in missing_domains:
            result = self._build_empty_result(domain)
            results.append(result)
        
        # Final results
        high_confidence_results = [r for r in results if r.confidence_score >= self.confidence_threshold]
        
        yield orjson.dumps({
            "type": "pipeline_complete",
            "message": "Research pipeline completed",
            "summary": {
                "total_domains": len(self.company_domains),
                "domains_analyzed": len(results),
                "high_confidence_matches": len(high_confidence_results),
                "avg_confidence": round(sum(r.confidence_score for r in results) / len(results), 2) if results else 0,
                "total_evidence": sum(len(r.findings.evidence) if r.findings else 0 for r in results),
                "processing_time": round(time.time() - (time.perf_counter() - self.metrics.start_time), 2)
            },
            "results": [r.model_dump() for r in results],
            "high_confidence_results": [r.model_dump() for r in high_confidence_results],
            "metrics": self.metrics.to_dict(),
            "timestamp": time.time()
        }).decode()
