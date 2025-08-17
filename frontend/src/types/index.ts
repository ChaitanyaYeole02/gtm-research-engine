// API Types for GTM Research Engine

export interface CompanyDomain {
  domain: string;
}

export interface ResearchRequest {
  research_goal: string;
  company_domains: string[];
  search_depth: "quick" | "standard" | "comprehensive";
  max_parallel_searches: number;
  confidence_threshold: number;
}

export interface Evidence {
  url: string;
  title: string;
  snippet: string;
  source_name: string;
  score: number;
}

export interface Findings {
  technologies: string[];
  evidence: Evidence[];
  signals_found: number;
}

export interface CompanyResearchResult {
  domain: string;
  confidence_score: number;
  evidence_sources: number;
  findings: Findings;
}

export interface ResearchResponse {
  research_id: string;
  total_companies: number;
  search_strategies_generated: number;
  total_searches_executed: number;
  processing_time_ms: number;
  results: CompanyResearchResult[];
  search_performance: {
    total_queries: number;
    successful_queries: number;
    failed_queries: number;
    avg_response_time_ms: number;
  };
}
