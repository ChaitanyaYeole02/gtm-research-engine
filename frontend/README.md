# GTM Research Engine - Frontend

A modern, responsive React-based frontend for the GTM Research Engine, built with Material-UI v7 and Vite.

## 🚀 Features

### **Search Interface**

- **Intelligent Search Input**: Large, prominent search field with search icon
- **Settings Configuration**: Tune button for advanced search parameters
- **Real-time Validation**: Input validation with user-friendly error messages
- **Responsive Design**: Mobile-first approach with breakpoint optimization

### **Advanced Settings**

- **Parallel Search Control**: Configure `max_parallel_searches` (1-10)
- **Company Domains**: Add/remove specific company domains for targeted research
- **Search Depth**: Choose between 'quick', 'standard', or 'comprehensive'
- **Confidence Threshold**: Set confidence level from 0.0 to 1.0

## 🛠️ Technology Stack

- **Framework**: React 18 with TypeScript
- **UI Library**: Material-UI (MUI) v7
- **Build Tool**: Vite 5.x
- **Styling**: CSS-in-JS with MUI's `sx` prop
- **State Management**: React hooks with custom logic
- **Type Safety**: Full TypeScript implementation

## 📦 Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🔧 Development

### **Available Scripts**

- `npm run dev` - Start development server (localhost:3000)
- `npm run build` - Build production bundle
- `npm run preview` - Preview production build locally
- `npm run start` - Alias for dev server

### **Development Server**

- **Port**: 3000
- **Hot Reload**: Enabled
- **TypeScript**: Real-time type checking
- **ESLint**: Code quality enforcement

## 🎨 Component Architecture

### **Data Flow**

1. **User Input** → SearchForm component
2. **Settings Configuration** → SettingsMenu component
3. **Form Submission** → useSearch hook
4. **API Call** → Backend research endpoint
5. **Results Display** → ResearchResults component

## 🔌 API Integration

### **Endpoint**

- **URL**: `http://localhost:8000/research/batch`
- **Method**: POST
- **Content-Type**: application/json

### **Request Format**

```typescript
{
  research_goal: string;
  company_domains: string[];
  search_depth: "quick" | "standard" | "comprehensive";
  max_parallel_searches: number;
  confidence_threshold: number;
}
```

### **Response Handling**

- **Success**: Display results in organized, tabbed interface
- **Error**: Show user-friendly error messages
- **Loading**: Circular progress and disabled states

## 🎨 Design System

### **Color Palette**

- **Primary**: Orange gradient (#FF7A00 → #E65C00)
- **Background**: Subtle off-white (hsl(0, 0%, 98%))
- **Text**: Dark grays with proper contrast
- **Accents**: Material-UI semantic colors

## 🔮 Future Enhancements

### **Planned Features**

- **Real-time Updates**: WebSocket integration for live research progress
- **Export Options**: PDF/CSV result export
- **Search History**: User research query history
- **Advanced Filtering**: Result filtering and sorting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🔗 Related Links

- **Backend API**: [Backend Documentation](../backend/README.md)
- **Project Overview**: [Main README](../README.md)
