import React from "react";

import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import Divider from "@mui/material/Divider";
import FormControl from "@mui/material/FormControl";
import MenuItem from "@mui/material/MenuItem";
import Popover from "@mui/material/Popover";
import Select from "@mui/material/Select";
import Slider from "@mui/material/Slider";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";

import { SearchSettings } from "../../types/settings";

interface SettingsMenuProps {
  open: boolean;
  anchorEl: HTMLElement | null;
  onClose: () => void;
  settings: SearchSettings;
  onSettingsChange: (settings: SearchSettings) => void;
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

export const SettingsMenu: React.FC<SettingsMenuProps> = ({
  open,
  anchorEl,
  onClose,
  settings,
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
    <Popover
      open={open}
      anchorEl={anchorEl}
      onClose={onClose}
      anchorOrigin={{
        vertical: "top",
        horizontal: "right",
      }}
      transformOrigin={{
        vertical: "top",
        horizontal: "left",
      }}
    >
      <Box
        sx={{
          p: 3,
          minWidth: 350,
          maxHeight: "70vh",
          overflowY: "auto",
        }}
      >
        <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
          Search Configuration
        </Typography>

        <Stack spacing={3}>
          {/* Max Parallel Searches */}
          <Box>
            <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>
              Max Parallel Searches
            </Typography>
            <TextField
              type="number"
              size="small"
              fullWidth
              value={maxSearchesInput}
              onChange={onMaxSearchesChange}
              error={maxSearchesError}
              helperText={
                maxSearchesError
                  ? "Please enter a value between 1 and 10"
                  : "Valid range: 1-10 searches"
              }
              inputProps={{ min: 1, max: 10 }}
              variant="outlined"
            />
          </Box>

          {/* Search Depth */}
          <Box>
            <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>
              Search Depth
            </Typography>
            <FormControl fullWidth size="small">
              <Select
                value={settings.searchDepth}
                onChange={(e) =>
                  onSearchDepthChange(
                    e.target.value as "quick" | "standard" | "comprehensive"
                  )
                }
              >
                <MenuItem value="quick">Quick</MenuItem>
                <MenuItem value="standard">Standard</MenuItem>
                <MenuItem value="comprehensive">Comprehensive</MenuItem>
              </Select>
            </FormControl>
          </Box>

          {/* Confidence Threshold */}
          <Box>
            <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>
              Confidence Threshold: {settings.confidenceThreshold.toFixed(1)}
            </Typography>
            <Slider
              value={settings.confidenceThreshold}
              onChange={(_, newValue) => onConfidenceChange(newValue as number)}
              min={0}
              max={1}
              step={0.1}
              marks={[
                { value: 0, label: "0.0" },
                { value: 0.5, label: "0.5" },
                { value: 1, label: "1.0" },
              ]}
              sx={{ mt: 1 }}
            />
          </Box>

          <Divider />

          {/* Company Domains */}
          <Box>
            <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>
              Company Domains
            </Typography>
            <TextField
              size="small"
              fullWidth
              placeholder="Add domain (e.g. stripe.com, paypal.com...)"
              value={newDomain}
              onChange={(e) => onDomainChange(e.target.value)}
              onKeyPress={onKeyPress}
              variant="outlined"
              InputProps={{
                endAdornment: (
                  <Button
                    size="small"
                    onClick={onAddDomain}
                    disabled={!newDomain.trim()}
                  >
                    Add
                  </Button>
                ),
              }}
            />

            {settings.companyDomains.length > 0 && (
              <Box sx={{ mt: 2, display: "flex", flexWrap: "wrap", gap: 1 }}>
                {settings.companyDomains.map((domain, index) => (
                  <Chip
                    key={index}
                    label={domain}
                    size="small"
                    onDelete={() => onRemoveDomain(domain)}
                    color="primary"
                    variant="outlined"
                  />
                ))}
              </Box>
            )}
          </Box>
        </Stack>
      </Box>
    </Popover>
  );
};
