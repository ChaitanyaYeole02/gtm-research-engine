# GTM Research Engine

A comprehensive, AI-powered company research platform that aggregates data from multiple sources to provide deep insights into companies, technologies, and market trends.

## 🏗️ Overall Architecture

## 🚀 System Overview

The GTM Research Engine is a full-stack application that combines:

- **Backend**: FastAPI-powered research engine with multi-source data aggregation
- **Frontend**: Modern React interface with Material-UI v7 and TypeScript
- **Real-time Processing**: Streaming research results with SSE (Server-Sent Events)
- **Multi-source Data**: Google Search, News, Jobs, and Company databases
- **AI-Powered Analysis**: Intelligent query generation and confidence scoring

## 🔄 Data Flow Architecture

```
User Input → Frontend → Backend API → Research Pipeline → Data Sources
    ↓           ↓           ↓           ↓              ↓
Search Query → React UI → FastAPI → Query Generator → Google/News/Jobs
    ↓           ↓           ↓           ↓              ↓
Settings → State Mgmt → Validation → Research Engine → Company Data
    ↓           ↓           ↓           ↓              ↓
Results ← Tabbed UI ← JSON Response ← Aggregated Data ← Raw Sources
```

## 🎯 Key Features

### **Research Capabilities**

- **Multi-source Research**: Google Search, News APIs, Job boards, Company databases
- **Intelligent Query Generation**: AI-powered search strategy creation
- **Parallel Processing**: Configurable concurrent search execution
- **Confidence Scoring**: AI-based result relevance assessment
- **Real-time Streaming**: Live research progress updates

## 🛠️ Technology Stack

### **Backend**

- **Framework**: FastAPI (Python 3.11+)
- **Database**: Redis for caching and session management
- **Async Processing**: asyncio for concurrent operations
- **Data Sources**: Google Search, News APIs, Job platforms
- **AI Integration**: Gemini 2.5 Flash for query generation

### **Frontend**

- **Framework**: React 18 with TypeScript
- **UI Library**: Material-UI (MUI) v7
- **Build Tool**: Vite 5.x
- **State Management**: React hooks with custom logic
- **Styling**: CSS-in-JS with MUI's sx prop

### **Infrastructure**

- **API**: RESTful endpoints with ORJSON responses
- **Streaming**: Server-Sent Events (SSE) for real-time updates
- **Caching**: Redis-based result caching
- **Monitoring**: Performance metrics and error tracking

## 🚀 Quick Start

### **Prerequisites**

- Python 3.11+
- Node.js 18+
- Redis server
- API keys for data sources

### **Backend Setup**

```bash
cd backend
pip install -e .
uvicorn app.server:app --reload --port 8000
```

### **Frontend Setup**

```bash
cd frontend
npm install
npm run dev
```

### **Access the Application**

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🔌 API Endpoints

### **Core Research**

- `POST /research/batch` - Batch research execution
- `POST /research/batch/stream` - Streaming research with real-time updates

### **Request Format**

```json
{
  "research_goal": "Find fintech companies using AI for fraud detection",
  "company_domains": ["stripe.com", "paypal.com"],
  "search_depth": "standard",
  "max_parallel_searches": 5,
  "confidence_threshold": 0.7
}
```

### **Response Structure**

```json
{
  "research_id": "uuid",
  "total_companies": 2,
  "search_strategies_generated": 4,
  "total_searches_executed": 8,
  "processing_time_ms": 14016,
  "results": [...],
  "search_performance": {...}
}
```

## 🔍 Research Pipeline

### **1. Query Generation**

- AI-powered search strategy creation
- Multi-approach query formulation
- Search depth optimization

### **2. Parallel Execution**

- Concurrent data source queries
- Configurable parallelism (1-10)
- Resource management and rate limiting

### **3. Data Aggregation**

- Multi-source result collection
- Duplicate detection and removal
- Evidence correlation and scoring

### **4. Confidence Assessment**

- AI-based relevance scoring
- Source credibility weighting
- Result quality validation

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

### **Development Setup**

1. Fork the repository
2. Create a feature branch
3. Set up development environment
4. Make your changes
5. Add tests and documentation
6. Submit a pull request

### **Code Standards**

- **Python**: PEP 8 compliance, type hints
- **TypeScript**: Strict mode, comprehensive interfaces
- **Testing**: Unit tests for critical functions
- **Documentation**: Clear docstrings and README updates

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Documentation Links

- **Frontend**: [Frontend README](frontend/README.md)
- **Backend**: [Backend README](backend/README.md)
- **API Docs**: Available at `/docs` when backend is running
- **Architecture**: See architecture diagrams above

---
