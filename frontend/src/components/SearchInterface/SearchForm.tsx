import React from "react";

import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import SearchIcon from "@mui/icons-material/Search";

interface SearchFormProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  disabled?: boolean;
}

export const SearchForm: React.FC<SearchFormProps> = ({
  searchQuery,
  onSearchChange,
  disabled = false,
}) => {
  return (
    <Box sx={{ position: "relative" }}>
      <SearchIcon
        sx={{
          position: "absolute",
          left: 14,
          top: "50%",
          transform: "translateY(-50%)",
          color: disabled ? "text.disabled" : "text.secondary",
          fontSize: "1.25rem",
          zIndex: 1,
        }}
      />
      <TextField
        fullWidth
        value={searchQuery}
        onChange={(e) => onSearchChange(e.target.value)}
        placeholder="Enter your research goal (e.g., 'Find fintech companies using AI for fraud detection')"
        variant="outlined"
        size="medium"
        disabled={disabled}
        sx={{
          "& .MuiOutlinedInput-root": {
            fontSize: "1rem",
            padding: "4px 14px",
            paddingLeft: "48px",
            "& input": {
              padding: "16px 0",
            },
            "&.Mui-disabled": {
              backgroundColor: "#f5f5f5",
              "& input": {
                color: "#666666",
              },
            },
          },
        }}
      />
    </Box>
  );
};
