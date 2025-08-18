import React from "react";

import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Collapse from "@mui/material/Collapse";
import Divider from "@mui/material/Divider";
import IconButton from "@mui/material/IconButton";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import Typography from "@mui/material/Typography";
import Link from "@mui/material/Link";

import BusinessIcon from "@mui/icons-material/Business";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import LinkIcon from "@mui/icons-material/Link";
import PsychologyIcon from "@mui/icons-material/Psychology";
import SourceIcon from "@mui/icons-material/Source";
import SpeedIcon from "@mui/icons-material/Speed";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";

import { ResearchResults, CompanyResearchResult } from "../../types/search";

interface ResearchResultsProps {
  results: ResearchResults;
  onClear: () => void;
}

export const ResearchResultsComponent: React.FC<ResearchResultsProps> = ({
  results,
  onClear,
}) => {
  const [expandedCompany, setExpandedCompany] = React.useState<string | null>(
    null
  );

  const toggleCompanyExpansion = (domain: string) => {
    setExpandedCompany(expandedCompany === domain ? null : domain);
  };

  const formatProcessingTime = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  return (
    <Box sx={{ mt: 4 }}>
      {/* Header Stats */}
      <Paper
        elevation={2}
        sx={{
          p: 3,
          mb: 3,
          background: "linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)",
          border: "1px solid #dee2e6",
        }}
      >
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: {
              xs: "1fr",
              sm: "repeat(2, 1fr)",
              md: "repeat(4, 1fr)",
            },
            gap: 3,
          }}
        >
          <Box sx={{ textAlign: "center" }}>
            <BusinessIcon sx={{ fontSize: 40, color: "primary.main", mb: 1 }} />
            <Typography variant="h4" color="primary.main" fontWeight="bold">
              {results.total_companies}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Companies Analyzed
            </Typography>
          </Box>
          <Box sx={{ textAlign: "center" }}>
            <PsychologyIcon
              sx={{ fontSize: 40, color: "secondary.main", mb: 1 }}
            />
            <Typography variant="h4" color="secondary.main" fontWeight="bold">
              {results.search_strategies_generated}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Search Strategies
            </Typography>
          </Box>
          <Box sx={{ textAlign: "center" }}>
            <SpeedIcon sx={{ fontSize: 40, color: "info.main", mb: 1 }} />
            <Typography variant="h4" color="info.main" fontWeight="bold">
              {results.total_searches_executed}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Searches Executed
            </Typography>
          </Box>
          <Box sx={{ textAlign: "center" }}>
            <TrendingUpIcon
              sx={{ fontSize: 40, color: "success.main", mb: 1 }}
            />
            <Typography variant="h4" color="success.main" fontWeight="bold">
              {formatProcessingTime(results.processing_time_ms)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Processing Time
            </Typography>
          </Box>
        </Box>

        {/* Performance Metrics */}
        <Divider sx={{ my: 2 }} />
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <Box>
            <Typography variant="body2" color="text.secondary">
              Performance:{" "}
              {results.search_performance.queries_per_second.toFixed(2)}{" "}
              queries/sec
            </Typography>
            {results.search_performance.failed_requests > 0 && (
              <Typography variant="body2" color="error.main">
                {results.search_performance.failed_requests} failed requests
              </Typography>
            )}
          </Box>
          <Typography variant="caption" color="text.secondary">
            Research ID: {results.research_id}
          </Typography>
        </Box>
      </Paper>

      {/* Company Results */}
      <Stack spacing={3}>
        {results.results.map((company, index) => (
          <CompanyResultCard
            key={company.domain}
            company={company}
            isExpanded={expandedCompany === company.domain}
            onToggleExpansion={() => toggleCompanyExpansion(company.domain)}
          />
        ))}
      </Stack>

      {/* Clear Results Button */}
      <Box sx={{ mt: 4, textAlign: "center" }}>
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ cursor: "pointer", "&:hover": { color: "primary.main" } }}
          onClick={onClear}
        >
          Start New Research
        </Typography>
      </Box>
    </Box>
  );
};

interface CompanyResultCardProps {
  company: CompanyResearchResult;
  isExpanded: boolean;
  onToggleExpansion: () => void;
}

const CompanyResultCard: React.FC<CompanyResultCardProps> = ({
  company,
  isExpanded,
  onToggleExpansion,
}) => {
  const [selectedTab, setSelectedTab] = React.useState(0);

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return "success";
    if (score >= 0.6) return "warning";
    return "error";
  };

  const getConfidenceLabel = (score: number) => {
    if (score >= 0.9) return "Very High";
    if (score >= 0.8) return "High";
    if (score >= 0.7) return "Good";
    if (score >= 0.6) return "Moderate";
    return "Low";
  };

  // Group evidence by source
  const evidenceBySource = company.findings.evidence.reduce((acc, evidence) => {
    if (!acc[evidence.source_name]) {
      acc[evidence.source_name] = [];
    }
    acc[evidence.source_name].push(evidence);
    return acc;
  }, {} as Record<string, typeof company.findings.evidence>);

  const sourceNames = Object.keys(evidenceBySource);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
  };

  return (
    <Card elevation={2} sx={{ border: "1px solid #e0e0e0" }}>
      <CardContent>
        {/* Company Header */}
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 2,
          }}
        >
          <Box>
            <Typography variant="h6" fontWeight="bold" color="primary.main">
              {company.domain}
            </Typography>
            <Box sx={{ display: "flex", gap: 1, mt: 1 }}>
              <Chip
                label={`${(company.confidence_score * 100).toFixed(
                  0
                )}% Confidence`}
                color={getConfidenceColor(company.confidence_score) as any}
                size="small"
                variant="outlined"
              />
              <Chip
                label={getConfidenceLabel(company.confidence_score)}
                color={getConfidenceColor(company.confidence_score) as any}
                size="small"
              />
              <Chip
                label={`${company.evidence_sources} Sources`}
                color="info"
                size="small"
                variant="outlined"
              />
            </Box>
          </Box>
          <IconButton onClick={onToggleExpansion} size="small">
            {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
        </Box>

        {/* Technologies Found */}
        {company.findings.technologies.length > 0 && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Technologies & Signals Found:
            </Typography>
            <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
              {company.findings.technologies.map((tech, index) => (
                <Chip
                  key={index}
                  label={tech}
                  size="small"
                  variant="outlined"
                  sx={{ backgroundColor: "#f8f9fa" }}
                />
              ))}
            </Box>
          </Box>
        )}

        {/* Evidence Sources with Tabs */}
        <Collapse in={isExpanded}>
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Evidence Sources ({company.findings.evidence.length} found):
            </Typography>

            {/* Tabs for different sources */}
            <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 2 }}>
              <Tabs
                value={selectedTab}
                onChange={handleTabChange}
                variant="scrollable"
                scrollButtons="auto"
                sx={{
                  "& .MuiTab-root": {
                    minWidth: "auto",
                    px: 2,
                    py: 1,
                    fontSize: "0.875rem",
                    textTransform: "none",
                    fontWeight: 500,
                  },
                }}
              >
                {sourceNames.map((sourceName, index) => (
                  <Tab
                    key={sourceName}
                    label={
                      <Box
                        sx={{ display: "flex", alignItems: "center", gap: 1 }}
                      >
                        <SourceIcon sx={{ fontSize: 16 }} />
                        <span>{sourceName}</span>
                        <Chip
                          label={evidenceBySource[sourceName].length}
                          size="small"
                          variant="outlined"
                          sx={{ fontSize: "0.75rem", height: 20 }}
                        />
                      </Box>
                    }
                    sx={{ textTransform: "none" }}
                  />
                ))}
              </Tabs>
            </Box>

            {/* Tab Content */}
            {sourceNames.map((sourceName, tabIndex) => (
              <Box
                key={sourceName}
                role="tabpanel"
                hidden={selectedTab !== tabIndex}
                sx={{ display: selectedTab === tabIndex ? "block" : "none" }}
              >
                <Stack spacing={2}>
                  {evidenceBySource[sourceName].map((evidence, index) => (
                    <Paper
                      key={index}
                      variant="outlined"
                      sx={{ p: 2, backgroundColor: "#fafafa" }}
                    >
                      <Box sx={{ display: "flex", gap: 1, mb: 1 }}>
                        <SourceIcon
                          sx={{ fontSize: 16, color: "text.secondary" }}
                        />
                        <Chip
                          label={evidence.source_name}
                          size="small"
                          variant="outlined"
                          color="primary"
                        />
                      </Box>
                      <Typography
                        variant="subtitle2"
                        fontWeight="bold"
                        gutterBottom
                      >
                        {evidence.title}
                      </Typography>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ mb: 1 }}
                      >
                        {evidence.snippet}
                      </Typography>
                      <Link
                        href={evidence.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        sx={{
                          display: "flex",
                          alignItems: "center",
                          gap: 0.5,
                          color: "primary.main",
                          textDecoration: "none",
                          "&:hover": { textDecoration: "underline" },
                        }}
                      >
                        <LinkIcon sx={{ fontSize: 16 }} />
                        View Source
                      </Link>
                    </Paper>
                  ))}
                </Stack>
              </Box>
            ))}
          </Box>
        </Collapse>

        {/* Summary Stats */}
        <Box sx={{ mt: 2, pt: 2, borderTop: "1px solid #f0f0f0" }}>
          <Typography variant="body2" color="text.secondary">
            <strong>{company.findings.signals_found}</strong> signals detected
            across <strong>{company.evidence_sources}</strong> data sources
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};
