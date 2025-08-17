import React from "react";
import { TextField } from "@mui/material";
import { Search as SearchIcon } from "@mui/icons-material";

interface SearchFormProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
}

export const SearchForm: React.FC<SearchFormProps> = ({
  searchQuery,
  onSearchChange,
}) => {
  return (
    <TextField
      fullWidth
      value={searchQuery}
      onChange={(e) => onSearchChange(e.target.value)}
      placeholder="Enter your research goal (e.g., 'Find fintech companies using AI for fraud detection')"
      variant="outlined"
      size="medium"
      sx={{
        "& .MuiOutlinedInput-root": {
          fontSize: "1rem",
          padding: "4px 14px",
          "& input": {
            padding: "16px 0",
          },
        },
      }}
      InputProps={{
        startAdornment: (
          <SearchIcon
            sx={{
              color: "text.secondary",
              mr: 1,
              fontSize: "1.25rem",
            }}
          />
        ),
      }}
    />
  );
};
