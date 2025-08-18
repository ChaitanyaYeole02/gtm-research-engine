import { useState } from "react";

import { SearchSettings } from "../types/settings";

export const useSettings = () => {
  const [settingsAnchor, setSettingsAnchor] = useState<HTMLElement | null>(
    null
  );
  const [maxParallelSearches, setMaxParallelSearches] = useState<number>(3);
  const [maxSearchesInput, setMaxSearchesInput] = useState<string>("3");
  const [maxSearchesError, setMaxSearchesError] = useState<boolean>(false);
  const [companyDomains, setCompanyDomains] = useState<string[]>([]);
  const [searchDepth, setSearchDepth] = useState<
    "quick" | "standard" | "comprehensive"
  >("standard");
  const [confidenceThreshold, setConfidenceThreshold] = useState<number>(0.7);
  const [newDomain, setNewDomain] = useState<string>("");

  const handleSettingsClick = (event: React.MouseEvent<HTMLElement>) => {
    setSettingsAnchor(event.currentTarget);
  };

  const handleSettingsClose = () => {
    setSettingsAnchor(null);
  };

  const handleMaxSearchesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputValue = e.target.value;
    setMaxSearchesInput(inputValue);

    const numValue = parseInt(inputValue);

    if (isNaN(numValue) || inputValue === "") {
      setMaxSearchesError(false);
      return;
    }

    if (numValue < 1 || numValue > 10) {
      setMaxSearchesError(true);
    } else {
      setMaxSearchesError(false);
      setMaxParallelSearches(numValue);
    }
  };

  const handleAddDomain = () => {
    if (newDomain.trim() && !companyDomains.includes(newDomain.trim())) {
      setCompanyDomains([...companyDomains, newDomain.trim()]);
      setNewDomain("");
    }
  };

  const handleRemoveDomain = (domainToRemove: string) => {
    setCompanyDomains(
      companyDomains.filter((domain) => domain !== domainToRemove)
    );
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleAddDomain();
    }
  };

  const getSettings = (): SearchSettings => ({
    maxParallelSearches,
    companyDomains,
    searchDepth,
    confidenceThreshold,
  });

  return {
    settingsAnchor,
    maxParallelSearches,
    maxSearchesInput,
    maxSearchesError,
    companyDomains,
    searchDepth,
    confidenceThreshold,
    newDomain,
    handleSettingsClick,
    handleSettingsClose,
    handleMaxSearchesChange,
    handleAddDomain,
    handleRemoveDomain,
    handleKeyPress,
    setSearchDepth,
    setConfidenceThreshold,
    setNewDomain,
    getSettings,
  };
};
