"""
Enhanced streaming aggregator that uses fully dynamic LLM-driven keyword extraction.
Replaces hardcoded keyword lists with intelligent, goal-aware extraction.
"""

import asyncio
import time
from collections import defaultdict
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field

from app.models.response import CompanyResearchResult, Evidence, Findings
from app.services.extractor import Extractor, ExtractionStrategy

@dataclass
class EnhancedStreamingState:
    """Enhanced streaming state with dynamic analysis."""
    domain: str
    evidences_by_key: Dict[str, Evidence] = field(default_factory=dict)
    source_names: Set[str] = field(default_factory=set)
    extracted_signals: Set[str] = field(default_factory=set)
    goal_confidence: float = 0.0
    goal_match: bool = False
    analysis_reasoning: str = ""
    last_updated: float = field(default_factory=time.time)
    evidence_count: int = 0

@dataclass 
class EnhancedStreamUpdate:
    """Enhanced streaming update with goal-aware analysis."""
    event_type: str  # "evidence_added", "analysis_complete", "domain_complete"
    domain: str
    new_evidence: Optional[Evidence] = None
    current_result: Optional[CompanyResearchResult] = None
    signals: List[str] = field(default_factory=list)
    goal_confidence: float = 0.0
    goal_match: bool = False
    reasoning: str = ""
    completion_percentage: float = 0.0

class EnhancedStreamingAggregator:
    """
    Fully dynamic streaming aggregator with LLM-driven analysis.
    
    Key improvements:
    1. No hardcoded keywords - everything derived from research goal
    2. Context-aware technology extraction
    3. Goal-specific confidence scoring
    4. Intelligent reasoning for each company
    """
    
    def __init__(self, research_goal: str, confidence_threshold: float = 0.7):
        self.research_goal = research_goal
        self.confidence_threshold = confidence_threshold
        
        # Dynamic extraction system
        self.tech_extractor = DynamicTechExtractor()
        self.extraction_strategy: Optional[ExtractionStrategy] = None
        
        # Streaming state
        self.domain_states: Dict[str, EnhancedStreamingState] = {}
        self.total_expected_results = 0
        self.processed_results = 0
        
        # Thread safety
        self._lock = asyncio.Lock()
        self._strategy_initialized = False
    
    async def _ensure_strategy_initialized(self):
        """Ensure extraction strategy is generated from research goal."""
        if not self._strategy_initialized:
            self.extraction_strategy = await self.tech_extractor.generate_extraction_strategy(
                self.research_goal
            )
            self._strategy_initialized = True
            print(f"🎯 Dynamic strategy initialized for: {self.research_goal}")
            print(f"   Target Keywords: {self.extraction_strategy.target_keywords[:5]}...")  # Show first 5
    
    def _evidence_key(self, evidence: Evidence) -> str:
        """Generate unique key for evidence deduplication."""
        import hashlib
        content = f"{evidence.url}|{evidence.title}".lower().strip()
        return hashlib.sha1(content.encode()).hexdigest()
    
    async def add_evidence(self, domain: str, evidence: Evidence) -> EnhancedStreamUpdate:
        """
        Add evidence and perform dynamic analysis.
        
        This replaces the hardcoded keyword matching with intelligent LLM analysis.
        """
        async with self._lock:
            await self._ensure_strategy_initialized()
            
            # Initialize domain state
            if domain not in self.domain_states:
                self.domain_states[domain] = EnhancedStreamingState(domain=domain)
            
            state = self.domain_states[domain]
            
            # Check for duplicates
            evidence_key = self._evidence_key(evidence)
            if evidence_key in state.evidences_by_key:
                # Update existing if new one has higher score
                existing = state.evidences_by_key[evidence_key]
                if evidence.score > existing.score:
                    state.evidences_by_key[evidence_key] = evidence
                    state.last_updated = time.time()
            else:
                # Add new evidence
                state.evidences_by_key[evidence_key] = evidence
                state.evidence_count += 1
                state.source_names.add(evidence.source_name)
                state.last_updated = time.time()
            
            # Update global progress
            self.processed_results += 1
            
            return EnhancedStreamUpdate(
                event_type="evidence_added",
                domain=domain,
                new_evidence=evidence,
                signals=list(state.extracted_signals),
                goal_confidence=state.goal_confidence,
                goal_match=state.goal_match,
                reasoning=state.analysis_reasoning,
                completion_percentage=min(self.processed_results / max(self.total_expected_results, 1), 1.0)
            )
    
    async def analyze_domain_complete(self, domain: str) -> EnhancedStreamUpdate:
        """
        Perform complete analysis when all evidence for a domain is collected.
        This is where the magic happens - LLM analyzes all evidence together.
        """
        async with self._lock:
            await self._ensure_strategy_initialized()
            
            if domain not in self.domain_states:
                return EnhancedStreamUpdate(
                    event_type="analysis_complete",
                    domain=domain,
                    goal_match=False,
                    reasoning="No evidence found for domain"
                )
            
            state = self.domain_states[domain]
            evidences = list(state.evidences_by_key.values())
            
            if not evidences:
                return EnhancedStreamUpdate(
                    event_type="analysis_complete",
                    domain=domain,
                    goal_match=False,
                    reasoning="No valid evidence collected"
                )
            
            # Perform comprehensive LLM analysis
            analysis_result = await self.tech_extractor.analyze_company(
                self.research_goal, evidences
            )
            
            # Update state with analysis results
            state.extracted_signals = set(analysis_result["signals"])
            state.goal_confidence = analysis_result["confidence_score"]
            state.goal_match = analysis_result["goal_match"]
            state.analysis_reasoning = analysis_result["reasoning"]
            
            # Build final result
            current_result = self._build_result(state)
            
            return EnhancedStreamUpdate(
                event_type="analysis_complete",
                domain=domain,
                current_result=current_result,
                signals=analysis_result["signals"],
                goal_confidence=state.goal_confidence,
                goal_match=state.goal_match,
                reasoning=state.analysis_reasoning,
                completion_percentage=1.0
            )
    
    def _build_result(self, state: EnhancedStreamingState) -> CompanyResearchResult:
        """Build final company research result."""
        evidences = list(state.evidences_by_key.values())
        signals = sorted(list(state.extracted_signals))
        
        # Use LLM-determined goal match for specific findings
        # This is much more accurate than hardcoded rules
        findings = Findings(
            ai_fraud_detection=state.goal_match if "fraud" in self.research_goal.lower() else None,
            technologies=signals,  # Store all signals in technologies field for backward compatibility
            evidence=evidences,
            signals_found=len(signals)
        )
        
        return CompanyResearchResult(
            domain=state.domain,
            confidence_score=round(state.goal_confidence, 2),
            evidence_sources=len(state.source_names),
            findings=findings
        )
    
    async def get_high_confidence_domains(self, threshold: float = None) -> List[str]:
        """Get domains that meet the confidence threshold with goal matching."""
        threshold = threshold or self.confidence_threshold
        
        high_confidence = []
        for domain, state in self.domain_states.items():
            if state.goal_confidence >= threshold and state.goal_match:
                high_confidence.append(domain)
        
        return high_confidence
    
    def get_strategy_summary(self) -> Dict[str, any]:
        """Get summary of the dynamic extraction strategy being used."""
        if not self.extraction_strategy:
            return {"status": "not_initialized"}
        
        return {
            "research_goal": self.research_goal,
            "target_keywords": self.extraction_strategy.target_keywords,
            "context_phrases": self.extraction_strategy.context_phrases,
            "confidence_boosters": self.extraction_strategy.confidence_boosters,
            "total_keywords": len(self.extraction_strategy.target_keywords)
        }

# Usage example showing the power of dynamic extraction
async def demo_dynamic_vs_static():
    """Demonstrate the difference between dynamic and static keyword extraction."""
    
    # Different research goals that would need completely different keywords
    research_goals = [
        "Find fintech companies using AI for fraud detection",
        "Find healthcare companies using computer vision for medical imaging", 
        "Find e-commerce companies using recommendation engines for personalization",
        "Find automotive companies using IoT for predictive maintenance"
    ]
    
    for goal in research_goals:
        print(f"\n🎯 Research Goal: {goal}")
        print("=" * 80)
        
        # Create dynamic aggregator
        aggregator = EnhancedStreamingAggregator(goal)
        
        # Get the dynamic strategy
        strategy_summary = aggregator.get_strategy_summary()
        await aggregator._ensure_strategy_initialized()
        strategy_summary = aggregator.get_strategy_summary()
        
        print(f"📋 Dynamic Keywords Generated: {strategy_summary['target_keywords'][:10]}...")
        print(f"🎯 Context Phrases: {strategy_summary['context_phrases'][:3]}...")
        print(f"⚡ Total Keywords: {strategy_summary['total_keywords']}")
        
        print("\n💡 This is completely different for each research goal!")
        print("   No hardcoded lists needed - fully adaptive! 🚀")

if __name__ == "__main__":
    asyncio.run(demo_dynamic_vs_static())
