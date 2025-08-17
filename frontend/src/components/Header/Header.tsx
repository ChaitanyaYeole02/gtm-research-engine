import React from "react";
import { Typography } from "@mui/material";

export const Header: React.FC = () => {
  return (
    <>
      <Typography
        variant="h1"
        sx={{
          mb: 1,
          background: "linear-gradient(135deg, #1A1A1A 0%, #666666 100%)",
          backgroundClip: "text",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
          fontSize: { xs: "2rem", md: "2.5rem" },
        }}
      >
        GTM Research Engine
      </Typography>

      <Typography
        variant="body1"
        color="text.secondary"
        sx={{ mb: 4, fontSize: { xs: "1rem", md: "1.125rem" } }}
      >
        AI-powered company research across multiple data sources
      </Typography>
    </>
  );
};
