import React from "react";

import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import IconButton from "@mui/material/IconButton";

import TuneIcon from "@mui/icons-material/Tune";
import ArrowUpwardIcon from "@mui/icons-material/ArrowUpward";

interface SearchControlsProps {
  onSettingsClick: (event: React.MouseEvent<HTMLElement>) => void;
  onSubmit: () => void;
  disabled: boolean;
  isLoading: boolean;
}

export const SearchControls: React.FC<SearchControlsProps> = ({
  onSettingsClick,
  onSubmit,
  disabled,
  isLoading,
}) => {
  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        mt: 2,
      }}
    >
      <IconButton
        onClick={onSettingsClick}
        disabled={isLoading}
        sx={{
          color: isLoading ? "text.disabled" : "text.secondary",
          "&:hover": {
            color: isLoading ? "text.disabled" : "primary.main",
            backgroundColor: isLoading
              ? "transparent"
              : "rgba(255, 122, 0, 0.1)",
          },
          "&:disabled": {
            color: "text.disabled",
          },
        }}
      >
        <TuneIcon sx={{ fontSize: "1.3rem" }} />
      </IconButton>

      <Button
        type="submit"
        variant="contained"
        disabled={disabled}
        onClick={onSubmit}
        sx={{
          px: 4,
          py: 1.5,
          fontSize: "1rem",
          fontWeight: 600,
          background: disabled
            ? "#BDBDBD"
            : "linear-gradient(135deg, #FF7A00 0%, #E65C00 100%)",
          color: "#FFFFFF",
          "&:hover": {
            background: disabled
              ? "#BDBDBD"
              : "linear-gradient(135deg, #E65C00 0%, #CC5200 100%)",
          },
          "&:disabled": {
            background: "#BDBDBD",
            color: "#FFFFFF",
          },
        }}
        startIcon={
          isLoading ? (
            <CircularProgress
              size={20}
              thickness={4}
              sx={{ color: "#FFFFFF" }}
            />
          ) : (
            <ArrowUpwardIcon />
          )
        }
      >
        {isLoading ? "Researching..." : "Start Research"}
      </Button>
    </Box>
  );
};
