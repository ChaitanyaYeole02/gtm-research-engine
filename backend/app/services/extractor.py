"""
Fully dynamic LLM-powered keyword extraction system.
No hardcoded keywords - everything is generated from the research goal.
"""

import json
import asyncio
from typing import List, Set, Dict, Optional
from dataclasses import dataclass
from functools import lru_cache

import google.generativeai as genai
from dotenv import load_dotenv
import os

from app.decorators import rate_limited
from app.models.response import Evidence

load_dotenv()

@dataclass
class ExtractionStrategy:
    """Dynamic strategy for keyword extraction based on research goal."""
    target_keywords: List[str]
    context_phrases: List[str]
    confidence_boosters: List[str]

class Extractor:
    """
    Fully LLM-driven technology extraction:
    1. Analyze research goal to generate relevant keywords
    2. Use those keywords to extract technologies from evidence
    3. No hardcoded lists - completely adaptive
    """
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        
        # System instruction for keyword generation
        keyword_system_prompt = """
        You are a research strategy generator that analyzes research goals and creates comprehensive signal detection strategies for GTM intelligence.

        Your job is to identify ALL types of signals that would indicate a company matches the research criteria, including:
        - Technologies, tools, platforms, frameworks
        - Business activities, processes, use cases
        - Industry terms, domain-specific language
        - Product features, capabilities, offerings
        - Company attributes, characteristics, behaviors
        - Market positioning, messaging, value propositions

        THINK HOLISTICALLY:
        - What would this type of company DO, BUILD, OFFER, or SAY?
        - What technologies AND business processes would they have?
        - What language would they use in their marketing, job posts, or content?
        - What partnerships, integrations, or certifications might they mention?
        - What problems would they solve and how would they describe solutions?

        OUTPUT FORMAT:
        {
            "target_keywords": ["list of specific signals to look for - technologies, business terms, processes, offerings"],
            "context_phrases": ["phrases that indicate relevance to the goal"],
            "confidence_boosters": ["terms that strongly indicate a match"]
        }

        EXAMPLE:
        Research Goal: "Find companies using AI for customer service automation"
        Output: {
            "target_keywords": ["chatbot", "conversational ai", "customer service automation", "ai support", "automated ticketing", "sentiment analysis", "natural language processing", "support bot", "virtual assistant", "ai-powered helpdesk", "intelligent routing", "auto-response"],
            "context_phrases": ["automated customer support", "ai-driven service", "intelligent customer experience", "reduce support costs", "24/7 automated assistance"],
            "confidence_boosters": ["ai customer service platform", "automated support solution", "conversational customer experience"]
        }
        """
        
        # System instruction for evidence analysis
        evidence_system_prompt = """
        You are a technology intelligence analyst that extracts specific technologies from company evidence.

        You will be given:
        1. A research goal/criteria
        2. Relevant keywords to look for
        3. Company evidence (website content, job posts, news, etc.)

        Your task:
        - Extract SPECIFIC TECHNOLOGIES mentioned in the evidence
        - Focus on named tools, frameworks, platforms, programming languages
        - Avoid business descriptions or generic terms
        - Rate confidence based on strength and relevance of technology evidence
        - Determine if the company matches the research goal based on technologies found

        WHAT TO EXTRACT (Technologies):
        Programming languages: "Python", "JavaScript", "Go", "Rust"
        ML/AI frameworks: "TensorFlow", "PyTorch", "scikit-learn", "Keras"
        Databases: "PostgreSQL", "MongoDB", "Redis", "Elasticsearch"
        Cloud platforms: "AWS", "Google Cloud", "Azure", "Kubernetes"
        APIs/Services: "Stripe API", "Twilio", "SendGrid"
        Tools: "Docker", "Apache Kafka", "Jenkins", "Git"

        WHAT NOT TO EXTRACT (Business descriptions):
        "AI fraud detection tools" → Extract: "TensorFlow", "machine learning"
        "real-time analytics platform" → Extract: "Apache Kafka", "Redis"
        "cloud-native solutions" → Extract: "Kubernetes", "Docker"
        "payment processing capabilities" → Extract: "Stripe", "payment APIs"

        OUTPUT FORMAT:
        {
            "relevant_technologies": ["list of specific TECHNOLOGIES found - frameworks, tools, languages"],
            "goal_match_signals": ["list of evidence/signals that indicate the company matches the research goal"],
            "confidence_score": 0.0-1.0,
        }

        EXAMPLE:
        Research Goal: "Find companies using AI for fraud detection"
        Evidence: "We use TensorFlow for our fraud detection algorithms and Python for data processing"
        Output: {
            "relevant_technologies": ["TensorFlow", "Python"],
            "goal_match_signals": ["fraud detection algorithms", "AI-powered fraud prevention"],
            "confidence_score": 0.85,
        }
        """
        
        self.keyword_model = genai.GenerativeModel(
            model_name='gemini-2.5-flash-lite', 
            system_instruction=keyword_system_prompt, 
            generation_config=genai.GenerationConfig(temperature=0.7)
        )
        self.evidence_model = genai.GenerativeModel(
            model_name='gemini-2.5-flash-lite', 
            system_instruction=evidence_system_prompt, 
            generation_config=genai.GenerationConfig(temperature=0.7)
        )
        
        # Cache for extraction strategies
        self._strategy_cache: Dict[str, ExtractionStrategy] = {}
    
    @rate_limited("gemini")
    async def generate_extraction_strategy(self, research_goal: str) -> ExtractionStrategy:
        """Generate dynamic keyword strategy from research goal."""
        
        # Check cache first
        if research_goal in self._strategy_cache:
            return self._strategy_cache[research_goal]
        
        prompt = f"""
        RESEARCH GOAL: {research_goal}
        """
        
        try:
            response = self.keyword_model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean up JSON response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            result = json.loads(response_text)
            
            strategy = ExtractionStrategy(
                target_keywords=result.get("target_keywords", []),
                context_phrases=result.get("context_phrases", []),
                confidence_boosters=result.get("confidence_boosters", [])
            )
            
            # Cache the strategy
            self._strategy_cache[research_goal] = strategy
            return strategy
            
        except Exception as e:
            print(f"Strategy generation failed: {e}")
            # Fallback to empty strategy
            return ExtractionStrategy([], [], [], [])
    
    @rate_limited("gemini") 
    async def extract_technologies_from_evidence(
        self, 
        research_goal: str, 
        evidences: List[Evidence],
        strategy: ExtractionStrategy
    ) -> Dict[str, any]:
        """Extract technologies using the dynamic strategy."""
        
        if not evidences:
            return {
                "relevant_technologies": [],
                "confidence_score": 0.0,
                "goal_match_signals": [],
            }
        
        # Combine evidence into analyzable text
        combined_evidence = ""
        for i, evidence in enumerate(evidences[:3]):  # Limit to avoid token limits
            combined_evidence += f"""
Evidence {i+1}:
Title: {evidence.title}
Content: {evidence.snippet}

"""
        
        # Create context-aware prompt
        prompt = f"""
        RESEARCH GOAL: {research_goal}
        
        RELEVANT KEYWORDS TO LOOK FOR:
        {', '.join(strategy.target_keywords)}
        
        CONTEXT PHRASES THAT INDICATE RELEVANCE:
        {', '.join(strategy.context_phrases)}
        
        CONFIDENCE BOOSTERS:
        {', '.join(strategy.confidence_boosters)}
        
        COMPANY EVIDENCE:
        {combined_evidence}
        
        Based on the research goal and keyword strategy, analyze this company's evidence and extract relevant technologies. Consider both the presence of target keywords AND the context to determine if this company genuinely matches the research criteria.
        """
        
        try:
            response = self.evidence_model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean up JSON response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            result = json.loads(response_text)
            
            return {
                "relevant_technologies": result.get("relevant_technologies", []),
                "goal_match_signals": result.get("goal_match_signals", []),
                "confidence_score": result.get("confidence_score", 0.0),
            }
            
        except Exception as e:
            print(f"Evidence extraction failed: {e}")
            return {
                "relevant_technologies": [],
                "goal_match_signals": [],
                "confidence_score": 0.0,
            }
    
    async def analyze_company(self, research_goal: str, evidences: List[Evidence]) -> Dict[str, any]:
        """
        Complete analysis pipeline:
        1. Generate extraction strategy from research goal
        2. Extract technologies using that strategy
        3. Return comprehensive results
        """
        
        # Step 1: Generate dynamic keyword strategy
        strategy = await self.generate_extraction_strategy(research_goal)
        
        # Step 2: Extract technologies using the strategy
        extraction_result = await self.extract_technologies_from_evidence(
            research_goal, evidences, strategy
        )
        
        # Step 3: Return comprehensive result
        return {
            "technologies": extraction_result["relevant_technologies"],
            "goal_match_signals": extraction_result["goal_match_signals"],
            "confidence_score": extraction_result["confidence_score"],
        }

# Integration example for your existing system
class LLMDrivenStreamingAggregator:
    """
    Example of how to integrate dynamic extraction into your existing aggregator.
    """
    
    def __init__(self, research_goal: str, confidence_threshold: float = 0.7):
        self.research_goal = research_goal
        self.confidence_threshold = confidence_threshold
        self.tech_extractor = Extractor()
        
        # No hardcoded keywords needed!
        self.extraction_strategy = None
    
    async def initialize(self):
        """Initialize by generating the extraction strategy."""
        self.extraction_strategy = await self.tech_extractor.generate_extraction_strategy(
            self.research_goal
        )
        print(f"🎯 Generated strategy for '{self.research_goal}':")
        print(f"   Target Keywords: {self.extraction_strategy.target_keywords}")
        print(f"   Context Phrases: {self.extraction_strategy.context_phrases}")
    
    async def analyze_domain_evidence(self, domain: str, evidences: List[Evidence]) -> Dict[str, any]:
        """Analyze evidence for a specific domain using dynamic extraction."""
        
        if not self.extraction_strategy:
            await self.initialize()
        
        result = await self.tech_extractor.analyze_company(self.research_goal, evidences)
        
        return {
            "domain": domain,
            "signals": result["signals"],
            "confidence_score": result["confidence_score"],
            "goal_match": result["goal_match"],
            "reasoning": result["reasoning"],
            "meets_threshold": result["confidence_score"] >= self.confidence_threshold
        }
