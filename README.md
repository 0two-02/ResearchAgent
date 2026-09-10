# 🔬 ResearchPilot AI

### *From scattered research to actionable knowledge.*

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-blue)](https://react.dev)
[![IBM watsonx](https://img.shields.io/badge/IBM-watsonx.ai-purple)](https://www.ibm.com/watsonx)
[![ChromaDB](https://img.shields.io/badge/Vector-ChromaDB-orange)](https://www.trychroma.com)

---

## 📌 Project Overview

**ResearchPilot AI** is an intelligent, agentic AI research companion that helps students, researchers, and professionals discover, analyze, synthesize, and explore academic research at scale.

Instead of manually searching dozens of websites, downloading papers, reading them one by one, and guessing at research gaps — ResearchPilot automates the entire pipeline through **8 specialized AI agents powered by IBM watsonx.ai**.

---

## 🎯 Problem Statement

Academic research is fragmented, time-consuming, and cognitively overwhelming:

- Researchers spend 50%+ of their time finding and reading papers
- Identifying genuine research gaps requires deep domain expertise
- Literature reviews take weeks to write
- Emerging trends are hard to spot without analyzing hundreds of papers
- Cross-paper comparison is tedious and error-prone

---

## ✅ Solution

ResearchPilot AI addresses every one of these problems with an agentic AI workflow:

| Challenge | Solution |
|-----------|----------|
| Finding papers | Multi-source academic API search (arXiv, Semantic Scholar, OpenAlex, CrossRef) |
| Understanding papers | IBM watsonx.ai Paper Analysis Agent |
| Literature reviews | Literature Review Agent generating structured, cited reviews |
| Research gaps | Gap Detection Agent with evidence grounding |
| Future directions | Research Recommendation Agent |
| Trend identification | Trend Prediction Agent |
| Asking questions | RAG-powered Research Chat |

---

## 🌟 Key Features

### 🔍 Intelligent Multi-Source Research Search
- Searches arXiv, Semantic Scholar, OpenAlex, CrossRef in parallel
- Smart deduplication by DOI and title
- Relevance ranking using title overlap, citation count, and recency
- Filters by year, source, and field

### 🤖 8 Specialized AI Agents (IBM watsonx.ai)
1. **Research Planner Agent** – Understands intent, generates search strategy
2. **Research Discovery Agent** – Searches and collects papers
3. **Paper Analysis Agent** – Extracts problem, methodology, results, gaps
4. **Literature Review Agent** – Synthesizes multi-paper structured reviews
5. **Research Gap Agent** – Identifies understudied areas and contradictions
6. **Trend Prediction Agent** – AI-assisted forecasting from publication patterns
7. **Citation Analysis Agent** – Identifies influential and foundational papers
8. **Research Recommendation Agent** – Suggests specific future research directions

### 📄 Multimodal Document Processing
- Upload PDFs, TXT, Markdown, CSV files (up to 50 MB)
- Automatic text extraction, title/abstract detection
- Text chunking and embedding generation
- ChromaDB vector store indexing for semantic search

### 🧠 RAG Pipeline
- Every AI response is grounded in retrieved paper evidence
- Sources and evidence shown alongside every important answer
- Semantic search across all indexed documents and papers

### 📊 Interactive Research Dashboard
- Publication trend charts (bar/line)
- Keyword frequency visualization
- Topic cluster display
- Real-time stats: papers, topics, queries, gaps

### 💬 Research Chat
- Conversational assistant grounded in your research library
- Quick suggestion chips for common questions
- Source attribution for every answer

### 📝 Literature Review Generator
- Full structured review in markdown
- Exportable as `.md` file
- References listed with paper attribution

### 📊 Paper Comparison
- Side-by-side comparison table
- AI-generated comparison summary
- Export as CSV

### 💡 Research Ideas Generator
- Evidence-grounded future research suggestions
- Difficulty level assessment
- Methodology and dataset recommendations
- Export as JSON

---

## 🏗 Architecture

```
User Query
    ↓
Research Planner Agent (IBM watsonx.ai)
    ↓
Search Query Generator
    ↓
Academic Source APIs (arXiv | Semantic Scholar | OpenAlex | CrossRef)
    ↓
Deduplication + Relevance Ranking
    ↓
Paper Analysis Agent (IBM watsonx.ai)
    ↓
Research Knowledge Store (ChromaDB + SQLite)
    ↓
┌─────────────────┬─────────────────┐
↓                 ↓                 ↓
Literature     Research Gap      Trend
Review Agent   Agent             Agent
(IBM)          (IBM)             (IBM)
↓                 ↓                 ↓
└─────────────────┴─────────────────┘
    ↓
Research Recommendation Agent (IBM watsonx.ai)
    ↓
Visualization Layer (React + Recharts)
    ↓
User Dashboard
```

---

## 🤝 IBM Technology Integration

IBM technology is central to ResearchPilot AI, not peripheral:

| IBM Technology | Usage in ResearchPilot |
|----------------|------------------------|
| **IBM watsonx.ai** | Powers all 8 AI agents for research analysis and generation |
| **IBM Foundation Models** | `ibm/granite-13b-chat-v2` for language understanding and generation |
| **IBM Langflow** | Workflow orchestration JSON defining the complete agent pipeline |
| **IBM RAG** | Evidence-grounded responses using IBM models + ChromaDB |

### IBM Credentials Setup

```bash
# In your .env file:
IBM_API_KEY=your_api_key
IBM_PROJECT_ID=your_project_id
IBM_URL=https://us-south.ml.cloud.ibm.com
```

Get credentials at: [IBM watsonx.ai](https://www.ibm.com/products/watsonx-ai)

### Demo Mode
If IBM credentials are unavailable, the system automatically falls back to **Demo Mode** — producing realistic, structured AI responses so the application remains fully functional for demonstration.

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Recharts, React Router, Axios |
| Backend | FastAPI, Python 3.11, Pydantic v2 |
| Database | SQLAlchemy + SQLite (PostgreSQL-ready) |
| Vector Store | ChromaDB |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| AI/LLM | IBM watsonx.ai (Granite 13B) |
| Workflow | IBM Langflow (JSON workflow files) |
| Academic APIs | arXiv, Semantic Scholar, OpenAlex, CrossRef |
| PDF Processing | pdfplumber, PyPDF2 |
| Containers | Docker + Docker Compose |

---

## 📦 Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

### 1. Clone the repository

```bash
git clone https://github.com/your-username/researchpilot-ai.git
cd researchpilot-ai
```

### 2. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your IBM credentials and API keys
```

### 3. Backend Setup

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Frontend Setup

```bash
cd frontend
npm install
```

---

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `IBM_API_KEY` | Optional* | IBM watsonx.ai API key |
| `IBM_PROJECT_ID` | Optional* | IBM project ID |
| `IBM_URL` | Optional | IBM watsonx endpoint URL |
| `SEMANTIC_SCHOLAR_API_KEY` | Optional | Increases Semantic Scholar rate limits |
| `NCBI_API_KEY` | Optional | For PubMed access |
| `DATABASE_URL` | Optional | Defaults to SQLite |
| `DEMO_MODE` | Optional | Set `true` to use demo data |
| `CHROMA_PERSIST_DIRECTORY` | Optional | Vector DB path |

*Without IBM credentials, app runs in Demo Mode automatically.

---

## 🚀 Running the Application

### Option 1: Manual (Development)

**Start Backend:**
```bash
cd backend
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend runs at: http://localhost:8000
API Docs at: http://localhost:8000/api/docs

**Start Frontend:**
```bash
cd frontend
npm start
```

Frontend runs at: http://localhost:3000

### Option 2: Docker Compose

```bash
# Copy and configure environment
cp .env.example .env

# Start everything
docker-compose up --build

# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
```

---

## 🎭 Demo Mode

To run without external API keys:

```bash
# In .env:
DEMO_MODE=true
```

Or toggle per-request in the Workspace UI by enabling **Demo Mode** checkbox.

Demo mode:
- Loads 8 landmark AI/ML papers as sample data
- IBM agent responses use realistic pre-structured fallbacks
- All UI features work identically
- A visible "Demo Data" banner is shown to users

---

## 📡 API Documentation

Full interactive docs: `http://localhost:8000/api/docs`

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/research/search` | Full agentic research search |
| `POST` | `/api/research/analyze` | Analyze selected papers |
| `POST` | `/api/research/literature-review` | Generate literature review |
| `POST` | `/api/research/gaps` | Identify research gaps |
| `POST` | `/api/research/trends` | Analyze publication trends |
| `POST` | `/api/research/recommendations` | Get research recommendations |
| `POST` | `/api/research/compare` | Compare papers |
| `POST` | `/api/documents/upload` | Upload and process document |
| `POST` | `/api/documents/analyze` | AI analysis of uploaded doc |
| `POST` | `/api/chat` | Research assistant chat |
| `GET` | `/api/papers` | List all papers |
| `GET` | `/api/papers/{id}` | Get paper details |
| `GET` | `/api/dashboard` | Dashboard statistics |
| `GET` | `/api/health` | Health check |

### Example Search Request

```bash
curl -X POST http://localhost:8000/api/research/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Applications of AI in early disease detection",
    "sources": ["arxiv", "semantic_scholar", "openalex"],
    "max_results": 20,
    "demo_mode": false
  }'
```

---

## 🧪 Testing

```bash
cd backend
# Activate venv first

# Run all tests
pytest tests/ -v

# Run specific test category
pytest tests/test_researchpilot.py::test_deduplicate_by_doi -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=html
```

### Test Categories
- **Deduplication tests** – DOI and title-based dedup logic
- **Ranking tests** – Relevance scoring algorithm
- **Text chunking tests** – Document splitting
- **File validation tests** – Upload security checks
- **Embedding tests** – Vector generation
- **Agent tests** – AI agent output structure
- **Demo data tests** – Sample data integrity
- **API tests** – Endpoint health and responses

---

## 🌊 IBM Langflow Workflow

The file `langflow/research_agent.json` defines the complete Langflow workflow:

### Importing into Langflow

1. Install Langflow: `pip install langflow`
2. Start: `langflow run`
3. Open: `http://localhost:7860`
4. Import: Upload `langflow/research_agent.json`
5. Configure IBM credentials in the flow settings

### Workflow Nodes

| Node | Type | IBM Model |
|------|------|-----------|
| User Query | TextInput | — |
| Research Planner | PromptTemplate | Granite 13B |
| Search Query Generator | PromptTemplate | Granite 13B |
| Academic APIs | APICall | — |
| Deduplication | PythonFunction | — |
| Paper Analysis | PromptTemplate | Granite 13B |
| Knowledge Store | VectorStore (ChromaDB) | — |
| Literature Review | PromptTemplate | Granite 13B |
| Gap Agent | PromptTemplate | Granite 13B |
| Trend Agent | PromptTemplate | Granite 13B |
| Recommendation Agent | PromptTemplate | Granite 13B |
| Dashboard Output | OutputFormatter | — |

---

## 🎪 Hackathon Demonstration Guide

### 1-Minute Demo Script

1. **Open** http://localhost:3000
2. **Home page** – Show the "Before/After ResearchPilot" impact section
3. **Workspace** – Enter: *"Applications of AI in early disease detection"*
4. **Check sources**: arXiv, Semantic Scholar, OpenAlex
5. **Click Start Research** – Watch the 3-phase agent pipeline activate
6. **Results** – Show ranked paper cards with badges and citations
7. **AI Summary tab** – Show the research plan + summary
8. **Select 3 papers** → Click **"Find Research Gaps"**
9. **Gaps tab** – Show evidence-grounded gap cards
10. **Click Recommendations** – Show future research ideas
11. **Literature Review page** – Paste paper IDs, generate review
12. **Dashboard** – Show charts, topic clusters
13. **Paper detail** – Click a paper → AI Analysis
14. **Compare** – Select 2 papers → Compare
15. **Chat** – Ask "What are the major research gaps?"
16. **Upload** – Upload a PDF → Show indexing pipeline

### Key Selling Points for Judges

- ✅ Real IBM watsonx.ai integration (not fake)
- ✅ Real academic APIs (arXiv, Semantic Scholar, OpenAlex)
- ✅ 8 distinct AI agents with specific roles
- ✅ RAG pipeline with evidence attribution
- ✅ Full stack: React + FastAPI + SQLite + ChromaDB
- ✅ Demo mode for offline presentation
- ✅ Explainability on every AI output

---

## 📁 Project Structure

```
researchpilot-ai/
│
├── backend/
│   ├── main.py                           # FastAPI app entry point
│   ├── config.py                         # Configuration and environment
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── database/
│   │   ├── models.py                     # SQLAlchemy ORM models
│   │   └── session.py                    # DB session management
│   ├── schemas/
│   │   └── schemas.py                    # Pydantic request/response models
│   ├── api/
│   │   ├── research_routes.py            # Research endpoints
│   │   ├── document_routes.py            # Document upload endpoints
│   │   └── chat_routes.py                # Chat endpoint
│   └── services/
│       ├── academic_sources/
│       │   ├── base.py                   # Abstract source + StandardPaper
│       │   ├── arxiv_source.py           # arXiv API integration
│       │   ├── semantic_scholar_source.py # Semantic Scholar API
│       │   ├── crossref_source.py        # CrossRef API
│       │   ├── openalex_source.py        # OpenAlex API
│       │   └── aggregator.py             # Multi-source search + dedup
│       ├── document_processor/
│       │   └── extractor.py              # PDF/text/CSV extraction
│       ├── embeddings/
│       │   └── embedder.py               # Sentence transformer embeddings
│       ├── rag/
│       │   └── vector_store.py           # ChromaDB vector operations
│       ├── ibm/
│       │   └── watsonx_client.py         # IBM watsonx.ai integration
│       └── research_agents/
│           └── agents.py                 # All 8 AI agents
│
├── frontend/
│   ├── src/
│   │   ├── App.js                        # Router + Navbar
│   │   ├── index.css                     # Global styles
│   │   ├── pages/
│   │   │   ├── HomePage.js               # Hero + Impact + Workflow
│   │   │   ├── WorkspacePage.js          # Main research workspace
│   │   │   ├── DashboardPage.js          # Analytics dashboard
│   │   │   ├── LiteratureReviewPage.js   # Literature review generator
│   │   │   ├── ResearchIdeasPage.js      # Research recommendations
│   │   │   ├── UploadPage.js             # Document upload
│   │   │   ├── PaperDetailPage.js        # Individual paper analysis
│   │   │   └── ComparePage.js            # Paper comparison
│   │   ├── components/
│   │   │   ├── PaperCard.js              # Research paper card
│   │   │   ├── ChatPanel.js              # AI research chat
│   │   │   └── ResearchSummary.js        # Research plan + summary
│   │   └── services/
│   │       └── api.js                    # Axios API client
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
│
├── langflow/
│   └── research_agent.json               # IBM Langflow workflow definition
│
├── data/
│   └── demo/
│       └── demo_data.py                  # 8 landmark paper samples
│
├── tests/
│   └── test_researchpilot.py             # Comprehensive test suite
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🔮 Future Improvements

- [ ] Full PubMed integration
- [ ] PDF citation graph extraction (GROBID integration)
- [ ] Real-time paper alerts for new research
- [ ] Multi-user support with authentication
- [ ] Export to PDF using WeasyPrint/ReportLab
- [ ] Interactive D3.js citation network visualization
- [ ] LangChain/LlamaIndex integration for more complex RAG
- [ ] Support for IBM watsonx.governance for AI transparency
- [ ] Collaborative research workspaces
- [ ] Browser extension for saving papers

---

## 📜 License

MIT License — see LICENSE file.

---

## 🙏 Acknowledgments

- IBM Research for watsonx.ai foundation models
- arXiv for open academic paper access
- Semantic Scholar for the research graph API
- OpenAlex for open scholarly metadata
- The sentence-transformers team
- ChromaDB for the vector database
