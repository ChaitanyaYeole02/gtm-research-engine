import React from "react";

import { Paper, Stack } from "@mui/material";

import { SearchForm } from "./SearchForm";
import { SearchControls } from "./SearchControls";
import { SettingsMenu } from "./SettingsMenu";
import { SearchSettings } from "../../types/settings";

interface SearchInterfaceProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onSettingsClick: (event: React.MouseEvent<HTMLElement>) => void;
  onSubmit: () => void;
  isLoading: boolean;
  settings: SearchSettings;
  settingsAnchor: HTMLElement | null;
  onSettingsClose: () => void;
  maxSearchesInput: string;
  maxSearchesError: boolean;
  newDomain: string;
  onMaxSearchesChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onSearchDepthChange: (depth: "quick" | "standard" | "comprehensive") => void;
  onConfidenceChange: (value: number) => void;
  onDomainChange: (domain: string) => void;
  onAddDomain: () => void;
  onRemoveDomain: (domain: string) => void;
  onKeyPress: (e: React.KeyboardEvent) => void;
}

export const SearchInterface: React.FC<SearchInterfaceProps> = ({
  searchQuery,
  onSearchChange,
  onSettingsClick,
  onSubmit,
  isLoading,
  settings,
  settingsAnchor,
  onSettingsClose,
  maxSearchesInput,
  maxSearchesError,
  newDomain,
  onMaxSearchesChange,
  onSearchDepthChange,
  onConfidenceChange,
  onDomainChange,
  onAddDomain,
  onRemoveDomain,
  onKeyPress,
}) => {
  return (
    <Paper
      elevation={0}
      sx={{
        p: { xs: 3, md: 4 },
        mb: 45,
        borderRadius: 3,
        background: "#FFFFFF",
        border: "1px solid #E5E5E5",
        boxShadow:
          "0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06)",
      }}
    >
      <form
        onSubmit={(e) => {
          e.preventDefault();
          onSubmit();
        }}
      >
        <Stack spacing={3}>
          <SearchForm
            searchQuery={searchQuery}
            onSearchChange={onSearchChange}
            disabled={isLoading}
          />

          <SearchControls
            onSettingsClick={onSettingsClick}
            onSubmit={onSubmit}
            disabled={!searchQuery.trim() || isLoading}
            isLoading={isLoading}
          />
        </Stack>
      </form>

      <SettingsMenu
        open={Boolean(settingsAnchor)}
        anchorEl={settingsAnchor}
        onClose={onSettingsClose}
        settings={settings}
        onSettingsChange={() => {}} // This will be handled by the parent
        maxSearchesInput={maxSearchesInput}
        maxSearchesError={maxSearchesError}
        newDomain={newDomain}
        onMaxSearchesChange={onMaxSearchesChange}
        onSearchDepthChange={onSearchDepthChange}
        onConfidenceChange={onConfidenceChange}
        onDomainChange={onDomainChange}
        onAddDomain={onAddDomain}
        onRemoveDomain={onRemoveDomain}
        onKeyPress={onKeyPress}
      />
    </Paper>
  );
};
