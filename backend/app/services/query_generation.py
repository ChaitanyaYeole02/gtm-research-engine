import json
import os

from typing import List

import google.generativeai as genai

from dotenv import load_dotenv

from app.decorators import rate_limited
from app.models import QueryStrategy


load_dotenv()


class QueryGenerator:
    """LLM-powered query strategy generator using Google Gemini.

    Generates 8-12 diverse strategies across channels depending on search depth.
    """
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        
        system_instruction = """
You are a Multi-Source Query Strategy Generator for a GTM Research Engine. You convert research goals into targeted search strategies across multiple data sources to determine if companies match specific criteria.

CONTEXT:
The system will execute your generated strategies tempaltes across multiple company domains simultaneously using multiple data sources. Each strategy is optimized for its specific source type to gather comprehensive evidence about whether companies match the research criteria.
The system will dynamically substitute {DOMAIN} and {COMPANY_NAME} placeholders when executing searches.

SUPPORTED SOURCES & CHANNELS:

1. Company Websites (google_search)
Capabilities: Site-specific searches, file type searches, subdomain searches
Content Types: Company pages, blogs, documentation, case studies, job postings
Search Patterns:
- `site:{DOMAIN} [keywords]` - Search within company domain
- `site:{DOMAIN}/blog [keywords]` - Company blog content
- `site:{DOMAIN}/careers [keywords]` - Job postings and tech requirements
- `site:{DOMAIN} filetype:pdf [keywords]` - Technical documentation
- `site:{DOMAIN} (keyword1 OR keyword2) AND keyword3` - Boolean searches

2. News & PR Sources (news_search)
Capabilities: Company name searches, topic-based searches, date ranges
Content Types: Press releases, news articles, announcements, incident reports
Search Patterns:
- `{COMPANY_NAME} AND [keywords]` - Company-specific news
- `{COMPANY_NAME} "funding" OR "investment" OR "Series A"` - Funding news
- `{COMPANY_NAME} "security" OR "breach" OR "incident"` - Security incidents
- `{COMPANY_NAME} "partnership" AND [technology_keywords]` - Technology partnerships

3. External Web Sources (google_search)
Capabilities: External mentions, industry reports, third-party analysis
Content Types: Case studies, reviews, industry reports, social mentions
Search Patterns:
- `"{COMPANY_NAME}" AND [keywords] -site:{DOMAIN}` - External mentions
- `"case study" AND "{COMPANY_NAME}" AND [keywords]` - Customer case studies
- `"{COMPANY_NAME}" AND ("uses" OR "implements") AND [technology]` - Technology usage

4. Professional Networks (google_search)
Capabilities: Employee profiles, job postings, company updates
Content Types: LinkedIn posts, job requirements, employee backgrounds
Search Patterns:
- `site:linkedin.com/in/ "{COMPANY_NAME}" AND [keywords]` - Employee profiles
- `site:linkedin.com/company/{COMPANY_NAME} [keywords]` - Company updates

5. Jobs Search (jobs_search)
Capabilities: Job postings with TF-IDF content matching
Content Types: Job titles, job descriptions, requirements
Search Patterns:
- `[role] [primary_technology]` - Core role matching (e.g., "software engineer python")
- `[technology_stack] developer` - Technology-focused roles (e.g., "react node developer") 
- `[domain] [role]` - Domain-specific roles (e.g., "machine learning engineer")
- `[technology] [level]` - Experience-based matching (e.g., "kubernetes senior")

SEARCH DEPTH LEVELS:
- quick: 4-6 strategies (1 per major source, focus on highest-yield searches)
- standard: 7-10 strategies (1-2 per major source, diverse search types)
- comprehensive: 11-13 strategies (2-3 per major source, exhaustive coverage including edge cases)

STRATEGY GENERATION PRINCIPLES:

1. Source Optimization: Each strategy should be optimized for its specific source's capabilities and content types
2. Evidence Diversity: Generate strategies that find different types of evidence (direct mentions, job requirements, case studies, news, etc.)
3. Complementary Coverage: Strategies should complement each other to build a comprehensive evidence profile
4. Specificity: More specific queries often yield higher-quality evidence than broad searches

OUTPUT FORMAT:
Always respond with valid JSON following this exact schema:

```json
{
  "strategies": [
    {
      "channel": "google_search|news_search|jobs_search",
      "query_template": "search query with {DOMAIN} and/or {COMPANY_NAME} placeholders"
    }
  ],
}
```

EXAMPLE STRATEGY DISTRIBUTION:

For a comprehensive search about "companies using Kubernetes in production":

Company Website Strategies (3-4):
- Site search for Kubernetes documentation
- Job posting searches for Kubernetes engineers
- Blog searches for Kubernetes implementation posts
- Case study searches with Kubernetes mentions

News Database Strategies (3-4):
- Company announcements about Kubernetes adoption
- Press releases mentioning cloud infrastructure
- News about technical partnerships or migrations

External Web Strategies (3-4):
- Third-party case studies featuring the company
- Industry reports mentioning the company's tech stack
- Conference talks or presentations by company engineers

Professional Network Strategies (3-4):
- Employee profiles mentioning Kubernetes experience
- Job postings requiring Kubernetes skills
- Company updates about infrastructure changes

QUALITY CRITERIA:
- Each strategy should have a clear, specific purpose
- Queries should be realistic and executable
- Evidence types should be clearly defined and measurable
- Strategies should work together to build comprehensive company profiles
- Include both direct evidence (company says they use X) and indirect evidence (job postings, employee profiles, etc.)

Generate strategies that maximize information gathering while respecting rate limits and API constraints across all sources.
        """
        
        self.model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=system_instruction,
            generation_config=genai.GenerationConfig(temperature=0.7)
        )

    async def generate_strategies(
        self, research_goal: str, search_depth: str
    ) -> List[QueryStrategy]:
        """Generate query strategies using Google Gemini LLM."""
        try:
            strategies = await self._generate_with_llm(
                research_goal, search_depth
            )

            return strategies
        except Exception as e:
            print(f"LLM generation failed: {e}")
            return []

    @rate_limited("gemini")
    async def _generate_with_llm(
        self, research_goal: str, search_depth: str
    ) -> List[QueryStrategy]:
        """Generate strategies using GeminiLLM."""        
        user_prompt = f"""
        Research Goal: {research_goal}
        Search Depth: {search_depth}
        """

        # Generate response from Gemini
        response = self.model.generate_content(user_prompt)
        response_text = response.text.strip()

        # Parse JSON response (handle markdown formatting)
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:-3].strip()

        response_data = json.loads(response_text)

        
        # Extract strategies from the new response format
        strategies_list = response_data.get("strategies", [])
        
        # Pre-compute constants for faster validation
        required_fields = {"channel", "query_template"}
        supported_channels = {"google_search", "news_search", "jobs_search"}
        
        # Fast list comprehension with inline validation
        strategies = [
            QueryStrategy(
                channel=strategy_data["channel"],
                query_template=strategy_data["query_template"],
            )
            for strategy_data in strategies_list
            if self._is_valid_strategy(strategy_data, required_fields, supported_channels)
        ]

        return strategies

    def _is_valid_strategy(self, strategy_data: dict, required_fields: set, supported_channels: set) -> bool:
        """Fast inline validation - optimized for performance."""
        # Fast set membership checks
        if not required_fields.issubset(strategy_data.keys()):
            return False
        
        if strategy_data["channel"] not in supported_channels:
            return False
        
        # jobs_search doesn't need domain/company placeholders
        # It uses domain for company identification and query for TF-IDF search
        channel = strategy_data["channel"]
        template = strategy_data["query_template"]
        
        if channel == "jobs_search":
            return True  # Any template is valid for jobs_search
        else:
            # Other channels require domain/company placeholders
            return "{DOMAIN}" in template or "{COMPANY_NAME}" in template
