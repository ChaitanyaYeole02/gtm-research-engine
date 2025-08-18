export interface SearchQuery {
  research_goal: string;
  company_domains: string[];
  search_depth: "quick" | "standard" | "comprehensive";
  max_parallel_searches: number;
  confidence_threshold: number;
}

export interface SearchState {
  searchQuery: string;
  isLoading: boolean;
  results: ResearchResults | null;
  error: string | null;
}

export interface SearchFormProps {
  onSubmit: (query: SearchQuery) => void;
  isLoading: boolean;
}

// API Response Types
export interface Evidence {
  url: string;
  title: string;
  snippet: string;
  source_name: string;
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

export interface SearchPerformance {
  queries_per_second: number;
  failed_requests: number;
}

export interface ResearchResults {
  research_id: string;
  total_companies: number;
  search_strategies_generated: number;
  total_searches_executed: number;
  processing_time_ms: number;
  results: CompanyResearchResult[];
  search_performance: SearchPerformance;
}
