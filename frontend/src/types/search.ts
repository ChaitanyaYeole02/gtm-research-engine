export interface SearchQuery {
  query: string;
  maxParallelSearches: number;
  companyDomains: string[];
  searchDepth: "quick" | "standard" | "comprehensive";
  confidenceThreshold: number;
}

export interface SearchState {
  searchQuery: string;
  isLoading: boolean;
}

export interface SearchFormProps {
  onSubmit: (query: SearchQuery) => void;
  isLoading: boolean;
}
