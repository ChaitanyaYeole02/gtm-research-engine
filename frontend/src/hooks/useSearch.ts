import { useState } from "react";
import { SearchQuery } from "../types/search";

export const useSearch = () => {
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleSubmit = async (query: SearchQuery) => {
    if (!query.query.trim()) return;

    setIsLoading(true);
    // TODO: Implement API call to backend
    console.log("Searching for:", query.query);
    console.log("Configuration:", {
      maxParallelSearches: query.maxParallelSearches,
      companyDomains: query.companyDomains,
      searchDepth: query.searchDepth,
      confidenceThreshold: query.confidenceThreshold,
    });

    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
    }, 2000);
  };

  return {
    searchQuery,
    setSearchQuery,
    isLoading,
    handleSubmit,
  };
};
