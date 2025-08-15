import asyncio
import hashlib
import math
import re
import time
from collections import defaultdict
from typing import Dict, List, Set, AsyncGenerator, Optional
from dataclasses import dataclass, field

from app.models.response import CompanyResearchResult, Evidence, Findings


@dataclass
class StreamingState:
    """Tracks streaming aggregation state for a single domain."""
    domain: str
    evidences_by_key: Dict[str, Evidence] = field(default_factory=dict)
    source_names: Set[str] = field(default_factory=set)
    technologies: Set[str] = field(default_factory=set)
    last_updated: float = field(default_factory=time.time)
    evidence_count: int = 0
    

@dataclass 
class StreamUpdate:
    """Represents a streaming update event."""
    event_type: str  # "evidence_added", "domain_complete", "all_complete"
    domain: str
    new_evidence: Optional[Evidence] = None
    current_result: Optional[CompanyResearchResult] = None
    total_evidence: int = 0
    completion_percentage: float = 0.0


class StreamingAggregator:
    """
    Real-time streaming aggregator that processes evidence as it arrives.
    
    Features:
    - Live aggregation as results come in
    - Deduplication of overlapping data
    - Configurable technology detection
    - Real-time confidence scoring
    - Progress tracking
    """
    
    def __init__(
        self,
        research_goal: str,
        tech_keywords: Optional[List[str]] = None,
        confidence_threshold: float = 0.7
    ):
        self.research_goal = research_goal
        self.tech_keywords = tech_keywords or self._get_default_keywords()
        self.confidence_threshold = confidence_threshold
        
        # Streaming state
        self.domain_states: Dict[str, StreamingState] = {}
        self.completed_domains: Set[str] = set()
        self.total_expected_results = 0
        self.total_received_results = 0
        
        # Locks for thread safety
        self._lock = asyncio.Lock()
    
    def _get_default_keywords(self) -> List[str]:
        """Get default technology keywords - can be extended based on research goal."""
        base_keywords = [
            "kubernetes", "docker", "terraform", "aws", "gcp", "azure",
            "tensorflow", "pytorch", "scikit-learn", "machine learning", "ai",
            "stripe", "payment", "fraud detection", "risk scoring",
            "snowflake", "databricks", "spark", "kafka", "redis",
            "react", "node.js", "python", "golang", "rust"
        ]
        
        # Extend keywords based on research goal
        goal_lower = self.research_goal.lower()
        if "fraud" in goal_lower:
            base_keywords.extend(["fraud prevention", "anomaly detection", "risk management"])
        if "ai" in goal_lower or "ml" in goal_lower:
            base_keywords.extend(["neural network", "deep learning", "computer vision"])
        if "fintech" in goal_lower:
            base_keywords.extend(["blockchain", "cryptocurrency", "digital wallet"])
            
        return base_keywords
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        return re.sub(r"\s+", " ", text.strip().lower())
    
    def _evidence_key(self, evidence: Evidence) -> str:
        """Generate unique key for evidence deduplication."""
        return hashlib.sha1(
            f"{evidence.url}|{self._normalize_text(evidence.title)}".encode()
        ).hexdigest()
    
    def _extract_technologies(self, evidences: List[Evidence]) -> Set[str]:
        """Extract technologies from evidence using keyword matching."""
        technologies = set()
        
        for evidence in evidences:
            text_blob = f"{evidence.title} {evidence.snippet}".lower()
            
            for keyword in self.tech_keywords:
                if keyword.lower() in text_blob and keyword not in technologies:
                    technologies.add(keyword)
        
        return technologies
    
    def _compute_confidence(self, unique_sources: int, total_evidence: int, tech_count: int) -> float:
        """
        Compute confidence score based on evidence quality and quantity.
        
        Factors:
        - Number of unique sources (more sources = higher confidence)
        - Total evidence count (more evidence = higher confidence) 
        - Technology signals found (more relevant tech = higher confidence)
        """
        # Base confidence from sources and evidence
        source_factor = min(unique_sources / 3.0, 1.0)  # Normalize to 3+ sources
        evidence_factor = min(total_evidence / 10.0, 1.0)  # Normalize to 10+ pieces
        tech_factor = min(tech_count / 5.0, 1.0)  # Normalize to 5+ technologies
        
        # Weighted combination
        confidence = (
            source_factor * 0.4 +    # 40% from source diversity
            evidence_factor * 0.3 +  # 30% from evidence quantity  
            tech_factor * 0.3        # 30% from technology relevance
        )
        
        return max(0.0, min(1.0, confidence))
    
    def _build_result(self, state: StreamingState) -> CompanyResearchResult:
        """Build CompanyResearchResult from current state."""
        evidences = list(state.evidences_by_key.values())
        technologies = sorted(list(state.technologies))
        
        # Calculate confidence
        confidence = self._compute_confidence(
            unique_sources=len(state.source_names),
            total_evidence=len(evidences),
            tech_count=len(technologies)
        )
        
        # Research-goal specific findings
        goal_lower = self.research_goal.lower()
        ai_fraud_detection = any(
            term in " ".join(technologies).lower() 
            for term in ["fraud", "fraud detection", "anomaly detection", "risk scoring"]
        )
        
        findings = Findings(
            ai_fraud_detection=ai_fraud_detection,
            technologies=technologies,
            evidence=evidences,
            signals_found=len(technologies)
        )
        
        return CompanyResearchResult(
            domain=state.domain,
            confidence_score=round(confidence, 2),
            evidence_sources=len(state.source_names),
            findings=findings
        )
    
    async def add_evidence(self, domain: str, evidence: Evidence) -> StreamUpdate:
        """
        Add new evidence and return streaming update.
        
        This is the core method for real-time aggregation.
        """
        async with self._lock:
            # Initialize domain state if needed
            if domain not in self.domain_states:
                self.domain_states[domain] = StreamingState(domain=domain)
            
            state = self.domain_states[domain]
            
            # Check for duplicates
            evidence_key = self._evidence_key(evidence)
            if evidence_key in state.evidences_by_key:
                # Duplicate evidence - update existing if new one has higher score
                existing = state.evidences_by_key[evidence_key]
                if evidence.score > existing.score:
                    state.evidences_by_key[evidence_key] = evidence
                    state.last_updated = time.time()
            else:
                # New evidence
                state.evidences_by_key[evidence_key] = evidence
                state.evidence_count += 1
                state.source_names.add(evidence.source_name)
                state.last_updated = time.time()
                
                # Extract technologies from this evidence
                new_techs = self._extract_technologies([evidence])
                state.technologies.update(new_techs)
            
            # Track global progress
            self.total_received_results += 1
            
            # Build current result
            current_result = self._build_result(state)
            
            # Calculate completion percentage
            completion_pct = (
                self.total_received_results / max(self.total_expected_results, 1)
            ) * 100.0
            
            return StreamUpdate(
                event_type="evidence_added",
                domain=domain,
                new_evidence=evidence,
                current_result=current_result,
                total_evidence=self.total_received_results,
                completion_percentage=min(completion_pct, 100.0)
            )
    
    async def mark_domain_complete(self, domain: str) -> StreamUpdate:
        """Mark a domain as complete and return final result."""
        async with self._lock:
            self.completed_domains.add(domain)
            
            # Get final result
            if domain in self.domain_states:
                final_result = self._build_result(self.domain_states[domain])
            else:
                # Domain with no evidence
                final_result = CompanyResearchResult(
                    domain=domain,
                    confidence_score=0.0,
                    evidence_sources=0,
                    findings=Findings(
                        ai_fraud_detection=False,
                        technologies=[],
                        evidence=[],
                        signals_found=0
                    )
                )
            
            completion_pct = (len(self.completed_domains) / max(len(self.domain_states), 1)) * 100.0
            
            return StreamUpdate(
                event_type="domain_complete",
                domain=domain,
                current_result=final_result,
                total_evidence=self.total_received_results,
                completion_percentage=min(completion_pct, 100.0)
            )
    
    async def get_current_results(self) -> List[CompanyResearchResult]:
        """Get current aggregated results for all domains."""
        async with self._lock:
            results = []
            
            for domain, state in self.domain_states.items():
                result = self._build_result(state)
                results.append(result)
            
            return results
    
    async def is_complete(self) -> bool:
        """Check if all domains are complete."""
        async with self._lock:
            expected_domains = set(self.domain_states.keys())
            return len(self.completed_domains) >= len(expected_domains)
    
    def set_expected_results(self, total: int):
        """Set the total number of expected results for progress tracking."""
        self.total_expected_results = total
    
    async def get_high_confidence_domains(self) -> List[CompanyResearchResult]:
        """Get domains that meet the confidence threshold."""
        results = await self.get_current_results()
        return [
            result for result in results 
            if result.confidence_score >= self.confidence_threshold
        ]
