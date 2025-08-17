export interface SearchSettings {
  maxParallelSearches: number;
  companyDomains: string[];
  searchDepth: "quick" | "standard" | "comprehensive";
  confidenceThreshold: number;
}

export interface SettingsMenuProps {
  open: boolean;
  anchorEl: HTMLElement | null;
  onClose: () => void;
  settings: SearchSettings;
  onSettingsChange: (settings: SearchSettings) => void;
}
