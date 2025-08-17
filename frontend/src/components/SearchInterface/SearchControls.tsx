import React from "react";
import { Box, IconButton, Button } from "@mui/material";
import {
  Tune as TuneIcon,
  ArrowUpward as ArrowUpwardIcon,
} from "@mui/icons-material";

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
        sx={{
          color: "text.secondary",
          "&:hover": {
            color: "primary.main",
            backgroundColor: "rgba(255, 122, 0, 0.1)",
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
        startIcon={<ArrowUpwardIcon />}
      >
        {isLoading ? "Researching..." : "Start Research"}
      </Button>
    </Box>
  );
};
