import React from "react";

import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Container from "@mui/material/Container";
import Fade from "@mui/material/Fade";
import Typography from "@mui/material/Typography";

import { Header } from "./components/Header";
import { SearchInterface } from "./components/SearchInterface";
import { ResearchResultsComponent } from "./components/ResearchResults";
import { useSearch } from "./hooks/useSearch";
import { useSettings } from "./hooks/useSettings";

const App: React.FC = () => {
  const {
    searchQuery,
    setSearchQuery,
    isLoading,
    results,
    error,
    handleSubmit,
    clearResults,
  } = useSearch();
  const {
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
  } = useSettings();

  const onSubmit = () => {
    const settings = getSettings();
    handleSubmit({
      research_goal: searchQuery,
      company_domains: settings.companyDomains,
      search_depth: settings.searchDepth,
      max_parallel_searches: settings.maxParallelSearches,
      confidence_threshold: settings.confidenceThreshold,
    });
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        background: "rgba(250, 249, 245, 1)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 0,
      }}
    >
      <Container maxWidth="md">
        <Fade in timeout={800}>
          <Box sx={{ textAlign: "center" }}>
            <Header />

            {!results ? (
              <>
                <SearchInterface
                  searchQuery={searchQuery}
                  onSearchChange={setSearchQuery}
                  onSettingsClick={handleSettingsClick}
                  onSubmit={onSubmit}
                  isLoading={isLoading}
                  settings={{
                    maxParallelSearches,
                    companyDomains,
                    searchDepth,
                    confidenceThreshold,
                  }}
                  settingsAnchor={settingsAnchor}
                  onSettingsClose={handleSettingsClose}
                  maxSearchesInput={maxSearchesInput}
                  maxSearchesError={maxSearchesError}
                  newDomain={newDomain}
                  onMaxSearchesChange={handleMaxSearchesChange}
                  onSearchDepthChange={setSearchDepth}
                  onConfidenceChange={setConfidenceThreshold}
                  onDomainChange={setNewDomain}
                  onAddDomain={handleAddDomain}
                  onRemoveDomain={handleRemoveDomain}
                  onKeyPress={handleKeyPress}
                />

                {/* Example Queries */}
                <Box sx={{ mt: 4, pt: 3, borderTop: "1px solid #F0F0F0" }}>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ mb: 2 }}
                  >
                    Try these example queries:
                  </Typography>
                  <Box
                    sx={{
                      display: "flex",
                      flexWrap: "wrap",
                      gap: 2,
                      justifyContent: "center",
                    }}
                  >
                    {[
                      "Find SaaS companies in the AI space",
                      "Research fintech startups in Europe",
                      "Discover healthcare companies using blockchain",
                      "SaaS companies hiring ML engineers",
                    ].map((example, index) => (
                      <Button
                        key={index}
                        variant="outlined"
                        size="small"
                        onClick={() => setSearchQuery(example)}
                        sx={{
                          borderColor: "#E0E0E0",
                          color: "#666666",
                          "&:hover": {
                            borderColor: "#FF7A00",
                            color: "#FF7A00",
                          },
                        }}
                      >
                        {example}
                      </Button>
                    ))}
                  </Box>
                </Box>
              </>
            ) : (
              <ResearchResultsComponent
                results={results}
                onClear={clearResults}
              />
            )}

            {/* Error Display */}
            {error && (
              <Box
                sx={{
                  mt: 3,
                  p: 2,
                  backgroundColor: "#ffebee",
                  borderRadius: 1,
                  border: "1px solid #f44336",
                }}
              >
                <Typography color="error" variant="body2">
                  Error: {error}
                </Typography>
              </Box>
            )}
          </Box>
        </Fade>
      </Container>
    </Box>
  );
};

export default App;
