# GTM Research Engine - Frontend

Beautiful React TypeScript frontend for the GTM Research Engine, inspired by Claude.ai's clean design.

## Features

- **Modern UI/UX**: Clean, minimalist design inspired by Claude.ai
- **Material-UI**: Beautiful components with custom Claude-inspired theme
- **TypeScript**: Full type safety and better developer experience
- **Responsive Design**: Works perfectly on desktop and mobile devices
- **Orange Accent**: Custom orange color scheme matching Claude.ai branding

## Tech Stack

- React 18
- TypeScript
- Material-UI (MUI) v5
- Emotion (CSS-in-JS)
- Inter font family

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm start
```

The app will open at `http://localhost:3000`

### Available Scripts

- `npm start` - Run development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App (one-way operation)

## Design System

### Colors

- **Primary Orange**: `#FF7A00` (Claude's signature orange)
- **Background**: Pure white `#FFFFFF` with subtle gradients
- **Text**: Dark gray `#1A1A1A` for primary text
- **Secondary Text**: Medium gray `#666666`

### Typography

- **Font Family**: Inter (modern, readable)
- **Weights**: 300, 400, 500, 600, 700

### Components

- Clean input fields with subtle hover states
- Orange gradient buttons with smooth transitions
- Glassmorphism cards with backdrop blur
- Smooth fade-in animations

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/     # Reusable UI components
│   ├── types/         # TypeScript type definitions
│   ├── utils/         # Utility functions
│   ├── App.tsx        # Main application component
│   ├── index.tsx      # React entry point
│   └── theme.ts       # MUI theme configuration
├── package.json
└── tsconfig.json
```

## Future Enhancements

- Search results display
- Real-time streaming updates
- Company detail views
- Export functionality
- Dark mode support
- Advanced filtering options
