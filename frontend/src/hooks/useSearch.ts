import { useState } from "react";

import { ResearchResults, SearchQuery } from "../types/search";

export const useSearch = () => {
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [results, setResults] = useState<ResearchResults | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (query: SearchQuery) => {
    if (!query.research_goal.trim()) return;

    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await fetch("http://localhost:8000/research/batch", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(query),
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

      const data: ResearchResults = await response.json();
      setResults(data);
      console.log("Research results:", data);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "An error occurred";
      setError(errorMessage);
      console.error("Search error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const clearResults = () => {
    setResults(null);
    setError(null);
  };

  return {
    searchQuery,
    setSearchQuery,
    isLoading,
    results,
    error,
    handleSubmit,
    clearResults,
  };
};
