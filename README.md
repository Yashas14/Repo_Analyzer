<div align="center">

# 🔍 Repository Analyzer

### AI-Powered Repository Understanding & Documentation Tool

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

**Instantly understand any codebase.** Upload or clone a repository and get AI-powered analysis, interactive Q&A, architecture insights, and professional documentation — all in one tool.

[Features](#-features) • [Demo](#-demo) • [Quick Start](#-quick-start) • [API Reference](#-api-reference) • [Architecture](#-architecture)

</div>

---

## 📋 Table of Contents

- [Features](#-features)
- [Demo](#-demo)
- [Quick Start](#-quick-start)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [API Reference](#-api-reference)
- [Architecture](#-architecture)
- [Supported Languages](#-supported-languages)
- [AI Providers](#-ai-providers)
- [Docker Deployment](#-docker-deployment)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 🗂️ Repository Input
| Method | Description |
|--------|-------------|
| **ZIP Upload** | Upload any project as a ZIP file (up to 100MB) |
| **Git Clone** | Clone from GitHub, GitLab, or Bitbucket via HTTPS or SSH |

### 🧠 AI-Powered Analysis
- **Automated Structure Mapping** — Scans and maps the complete file/folder hierarchy
- **Module Detection** — Identifies logical modules (services, controllers, models, etc.)
- **Functionality Extraction** — Lists all major features with relevant code files
- **Architecture Recognition** — Detects patterns like MVC, microservices, layered architecture
- **Tech Stack Detection** — Identifies frameworks, libraries, and tools used
- **Dependency Analysis** — Parses package managers (npm, pip, Maven, Cargo, Go modules, etc.)

### 💬 Interactive Q&A
- Ask natural language questions about any repository
- Get contextual answers with file references and code snippets
- AI-generated suggested questions to explore the codebase
- Explain specific files or modules in detail

### 📄 Documentation Generation
| Format | Description |
|--------|-------------|
| **PDF** | Professional reports with styling, tables, and sections |
| **Markdown** | GitHub/GitLab-compatible documentation |
| **HTML** | Web-ready documentation with embedded styles |

### 🔐 Security
- Path traversal protection on ZIP extraction
- Input validation on all endpoints
- CORS configuration for controlled access
- No credential prompting during Git operations

---

## 🎬 Demo

### Home Page — Upload or Clone
Upload a ZIP file or paste a Git URL to get started instantly.

### Analysis Dashboard
View modules, functionalities, architecture patterns, tech stack, and dependencies at a glance.

### Interactive Chat
Ask questions about the codebase and get AI-powered answers with code references.

### Documentation Export
Generate and download professional documentation in PDF, Markdown, or HTML.

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.10+ |
| Node.js | 18+ |
| Git | 2.30+ |
| AI Provider | Gemini API key (free) or Ollama (local) |

### One-Command Setup (Docker)

```bash
# Clone the repository
git clone https://github.com/yourusername/repo-analyzer.git
cd repo-analyzer

# Create environment file
cp backend/.env.example backend/.env
# Edit backend/.env and add your GEMINI_API_KEY

# Start everything
docker-compose up --build
```

Access the app at **http://localhost** (frontend) and **http://localhost:8000/docs** (API docs).

### Manual Setup

<details>
<summary><b>Backend Setup</b></summary>

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your preferred AI provider settings

# Start the server
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
Interactive API docs at `http://localhost:8000/docs`

</details>

<details>
<summary><b>Frontend Setup</b></summary>

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

</details>

---

## 🛠️ Tech Stack

### Backend

| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance async web framework |
| **Pydantic** | Data validation and serialization |
| **Google Gemini** | AI analysis and code explanation (default) |
| **OpenAI GPT** | Alternative AI provider (paid) |
| **Ollama** | Free local AI inference |
| **ReportLab** | PDF document generation |
| **GitPython** | Git repository operations |
| **HTTPX** | Async HTTP client for API calls |
| **Uvicorn** | ASGI server |

### Frontend

| Technology | Purpose |
|------------|---------|
| **React 18** | UI framework with hooks |
| **Vite** | Fast build tool and dev server |
| **Tailwind CSS** | Utility-first CSS styling |
| **Zustand** | Lightweight state management |
| **Axios** | HTTP client with interceptors |
| **React Router v6** | Client-side routing |
| **React Syntax Highlighter** | Code display with 200+ language support |
| **React Markdown** | Markdown rendering |
| **React Dropzone** | Drag-and-drop file upload |
| **Lucide React** | Icon library |

---

## 📁 Project Structure

```
repo-analyzer/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app entry point & middleware
│   │   ├── config.py                  # Settings (AI providers, storage, CORS)
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py            # Pydantic request/response models
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── repository.py         # Upload, clone, file browsing endpoints
│   │   │   ├── analysis.py           # Analysis, explain, architecture endpoints
│   │   │   ├── chat.py               # Q&A, suggestions, file explanation
│   │   │   └── documentation.py      # Doc generation, download, preview
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── ai_service.py         # Multi-provider AI integration (singleton)
│   │       ├── repository_service.py # Git clone, ZIP extract, file ops
│   │       ├── analysis_service.py   # Structure analysis, module detection
│   │       ├── chat_service.py       # Q&A logic, context retrieval
│   │       └── documentation_service.py # PDF/MD/HTML generation
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── public/
│   │   └── favicon.svg
│   ├── src/
│   │   ├── components/
│   │   │   ├── Layout.jsx            # App shell with navigation
│   │   │   ├── FileUpload.jsx        # Drag-and-drop ZIP upload
│   │   │   ├── GitClone.jsx          # Git URL input with validation
│   │   │   ├── FileTree.jsx          # Interactive file browser
│   │   │   └── LoadingSpinner.jsx    # Loading states
│   │   ├── pages/
│   │   │   ├── HomePage.jsx          # Landing page with upload/clone
│   │   │   ├── AnalysisPage.jsx      # Analysis results dashboard
│   │   │   ├── ChatPage.jsx          # Interactive Q&A interface
│   │   │   ├── DocumentationPage.jsx # Doc generation & download
│   │   │   └── RepositoriesPage.jsx  # Repository list management
│   │   ├── services/
│   │   │   └── api.js                # Axios API client (all endpoints)
│   │   ├── store/
│   │   │   └── useStore.js           # Zustand global state
│   │   ├── App.jsx                    # Router and route definitions
│   │   ├── main.jsx                   # React entry point
│   │   └── index.css                  # Tailwind directives & global styles
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js                 # Vite config with proxy & code splitting
│   ├── tailwind.config.js
│   ├── nginx.conf                     # Production reverse proxy config
│   └── Dockerfile                     # Multi-stage build (Node → Nginx)
├── docker-compose.yml                 # Full-stack orchestration
└── README.md
```

---

## ⚙️ Installation

### Option 1: Docker (Recommended for Production)

```bash
git clone https://github.com/yourusername/repo-analyzer.git
cd repo-analyzer

# Configure AI provider
cp backend/.env.example backend/.env
# Edit backend/.env with your API key

# Build and start
docker-compose up --build
```

### Option 2: Manual Development Setup

#### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your preferred AI provider

# Run development server
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server (proxies API to backend)
npm run dev
```

---

## 🔧 Configuration

### Environment Variables (`backend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `AI_PROVIDER` | `gemini` | AI provider: `gemini`, `openai`, or `ollama` |
| `GEMINI_API_KEY` | — | Google Gemini API key ([get free key](https://aistudio.google.com/app/apikey)) |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Gemini model to use |
| `OPENAI_API_KEY` | — | OpenAI API key (if using OpenAI) |
| `OPENAI_MODEL` | `gpt-3.5-turbo` | OpenAI model to use |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.2` | Ollama model to use |
| `DEBUG` | `true` | Enable debug mode |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed CORS origins |
| `MAX_FILE_SIZE_MB` | `100` | Maximum upload file size |
| `UPLOAD_DIR` | `./uploads` | Directory for uploaded repos |
| `CLONE_DIR` | `./cloned_repos` | Directory for cloned repos |
| `REPORTS_DIR` | `./reports` | Directory for generated docs |

---

## 📡 API Reference

Base URL: `http://localhost:8000`

Interactive docs: `http://localhost:8000/docs` (Swagger UI)

### Repository Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/repository/upload` | Upload a ZIP file |
| `POST` | `/api/repository/clone` | Clone a Git repository |
| `GET` | `/api/repository/{id}/structure` | Get file tree structure |
| `GET` | `/api/repository/{id}/file?file_path=...` | Get file content |
| `GET` | `/api/repository/list` | List all repositories |
| `DELETE` | `/api/repository/{id}` | Delete a repository |

### Analysis Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/analysis/{id}/analyze` | Run full analysis |
| `GET` | `/api/analysis/{id}/status` | Check analysis status |
| `GET` | `/api/analysis/{id}/result` | Get complete analysis |
| `POST` | `/api/analysis/{id}/explain` | Get AI project explanation |
| `GET` | `/api/analysis/{id}/functionalities` | Get identified functionalities |
| `GET` | `/api/analysis/{id}/modules` | Get detected modules |
| `GET` | `/api/analysis/{id}/architecture` | Get architecture overview |
| `GET` | `/api/analysis/{id}/tech-stack` | Get technology stack |
| `GET` | `/api/analysis/{id}/dependencies` | Get dependencies |
| `POST` | `/api/analysis/{id}/explain-functionality` | Detailed functionality explanation |
| `POST` | `/api/analysis/{id}/explain-code` | Line-by-line code explanation |

### Chat Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat/{id}/ask` | Ask a question about the repo |
| `GET` | `/api/chat/{id}/suggestions` | Get suggested questions |
| `POST` | `/api/chat/{id}/explain-file` | Get file explanation |
| `POST` | `/api/chat/{id}/explain-module` | Get module explanation |
| `POST` | `/api/chat/{id}/find-files` | Find related files |

### Documentation Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/documentation/{id}/generate` | Generate documentation |
| `GET` | `/api/documentation/{id}/download` | Download generated docs |
| `GET` | `/api/documentation/{id}/preview` | Get HTML preview |
| `GET` | `/api/documentation/{id}/markdown` | Get markdown content |

### Example: Clone & Analyze a Repository

```bash
# 1. Clone a repository
curl -X POST http://localhost:8000/api/repository/clone \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/expressjs/express", "branch": "master"}'

# Response: {"repository_id": "abc-123", "name": "express", ...}

# 2. Run analysis
curl -X POST http://localhost:8000/api/analysis/abc-123/analyze

# 3. Ask a question
curl -X POST http://localhost:8000/api/chat/abc-123/ask \
  -H "Content-Type: application/json" \
  -d '{"repository_id": "abc-123", "message": "What does this project do?"}'

# 4. Generate documentation
curl -X POST http://localhost:8000/api/documentation/abc-123/generate \
  -H "Content-Type: application/json" \
  -d '{"repository_id": "abc-123", "format": "pdf"}'
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │   Home   │  │ Analysis │  │   Chat   │  │  Docs  │ │
│  │   Page   │  │   Page   │  │   Page   │  │  Page  │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───┬────┘ │
│       │              │              │             │       │
│  ┌────┴──────────────┴──────────────┴─────────────┴────┐ │
│  │              Zustand Store + Axios API               │ │
│  └─────────────────────────┬───────────────────────────┘ │
└────────────────────────────┼─────────────────────────────┘
                             │ HTTP (Vite Proxy / Nginx)
┌────────────────────────────┼─────────────────────────────┐
│                    Backend (FastAPI)                       │
│  ┌─────────────────────────┴───────────────────────────┐ │
│  │                    API Routers                        │ │
│  │  /repository  /analysis  /chat  /documentation       │ │
│  └───────┬──────────┬────────┬──────────┬──────────────┘ │
│          │          │        │          │                 │
│  ┌───────┴──────────┴────────┴──────────┴──────────────┐ │
│  │                   Services Layer                      │ │
│  │  RepositoryService  AnalysisService  ChatService      │ │
│  │  DocumentationService        AIService (singleton)    │ │
│  └──────────────────────────────────┬──────────────────┘ │
│                                     │                     │
│  ┌──────────────────────────────────┴──────────────────┐ │
│  │              AI Provider (configurable)               │ │
│  │     Google Gemini  │  OpenAI GPT  │  Ollama (local)  │ │
│  └──────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Input** → User uploads ZIP or provides Git URL
2. **Storage** → Repository cloned/extracted to local filesystem
3. **Analysis** → Service scans files, detects modules, parses dependencies
4. **AI Enhancement** → AI provider adds intelligent insights (architecture, summary)
5. **Results** → Cached as JSON alongside repository data
6. **Output** → Served via API, displayed in React UI, or exported as documentation

---

## 🌐 Supported Languages

The analyzer supports **100+ file extensions** across major programming languages:

| Category | Languages |
|----------|-----------|
| **Systems** | C, C++, Rust, Go, Zig, Nim |
| **JVM** | Java, Kotlin, Scala, Groovy, Clojure |
| **Web** | JavaScript, TypeScript, HTML, CSS, Vue, Svelte, Astro |
| **Python** | Python, Cython, Jupyter Notebooks |
| **Mobile** | Swift, Kotlin, Dart (Flutter) |
| **Scripting** | Ruby, PHP, Perl, Lua, R, Julia |
| **Functional** | Haskell, Elixir, Erlang, OCaml, Elm, PureScript |
| **.NET** | C#, F#, Visual Basic |
| **DevOps** | Dockerfile, Terraform, Ansible, Makefile |
| **Data** | SQL, GraphQL, Protocol Buffers |
| **Config** | JSON, YAML, TOML, XML, INI |
| **Documentation** | Markdown, reStructuredText, LaTeX |
| **Legacy** | COBOL, Fortran, Assembly |
| **Blockchain** | Solidity, Vyper |

---

## 🤖 AI Providers

### Google Gemini (Recommended — Free Tier)

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.0-flash
```

- **Free tier**: 15 requests/minute, 1500 requests/day
- **Setup**: Get key at [Google AI Studio](https://aistudio.google.com/app/apikey)
- **Models**: `gemini-2.0-flash` (fast), `gemini-1.5-pro` (detailed)

### Ollama (Free — Local)

```env
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

- **Completely free** — runs on your machine
- **Setup**: Install from [ollama.com](https://ollama.com/download), then `ollama pull llama3.2`
- **Models**: `llama3.2` (default), `codellama`, `mistral`

### OpenAI (Paid)

```env
AI_PROVIDER=openai
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-3.5-turbo
```

- **Paid**: ~$0.002 per 1K tokens (GPT-3.5)
- **Setup**: Get key at [OpenAI Platform](https://platform.openai.com/api-keys)
- **Models**: `gpt-3.5-turbo` (affordable), `gpt-4` (best quality)

### Fallback Mode

If no AI provider is configured, the app still works with basic structural analysis (module detection, dependency parsing, file statistics) — just without AI-generated insights.

---

## 🐳 Docker Deployment

### docker-compose.yml

The included `docker-compose.yml` runs:
- **Backend** on port `8000` with health checks
- **Frontend** on port `80` (Nginx serving built React + reverse proxy to backend)
- **Persistent volumes** for uploads, cloned repos, and reports

### Environment Variables for Docker

```bash
# Create .env in project root for docker-compose
AI_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
```

### Production Considerations

- Set `DEBUG=false` in production
- Configure proper `CORS_ORIGINS` for your domain
- Use a reverse proxy (Nginx/Traefik) with SSL for HTTPS
- Mount persistent volumes for data durability
- Set appropriate resource limits in docker-compose

---

## 📊 Usage Guide

### 1. Upload or Clone a Repository

**Via ZIP upload:**
- Drag & drop a `.zip` file onto the upload area
- Maximum file size: 100MB
- Supported: Any project structure

**Via Git clone:**
- Paste an HTTPS or SSH URL
- Supports: GitHub, GitLab, Bitbucket, any Git host
- Private repos: Use Personal Access Token in URL (`https://TOKEN@github.com/user/repo.git`)

### 2. Run Analysis

Click "Analyze" to start AI-powered analysis. The system will:
- Map the complete file structure
- Detect programming languages and line counts
- Identify modules and components
- Parse dependencies from package managers
- Use AI to identify functionalities and architecture

### 3. Explore Results

The Analysis page shows:
- **Overview**: Total files, lines of code, language distribution
- **Modules**: Detected components with file counts
- **Functionalities**: AI-identified features with descriptions
- **Architecture**: Pattern recognition and design insights
- **Tech Stack**: Frameworks and libraries detected
- **Dependencies**: Parsed from package.json, requirements.txt, etc.

### 4. Ask Questions

Use the Chat interface to ask anything:
- "What does this project do?"
- "How is authentication implemented?"
- "What design patterns are used?"
- "Explain the database layer"

### 5. Generate Documentation

Export professional documentation in your preferred format:
- **PDF** — Report-style with tables and formatting
- **Markdown** — Perfect for GitHub wikis or READMEs
- **HTML** — Standalone web page with styling

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run the backend tests: `cd backend && python -m pytest`
5. Test the frontend build: `cd frontend && npm run build`
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

### Development Tips

- Backend auto-reloads with `--reload` flag
- Frontend hot-reloads via Vite HMR
- API docs available at `/docs` (Swagger) and `/redoc` (ReDoc)
- Use Ollama for free local AI during development

---

## 📝 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ by [Yashas](https://github.com/yourusername)**

If you found this helpful, please ⭐ the repository!

</div>

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for AI features | Required |
| `AI_MODEL` | OpenAI model to use | `gpt-4` |
| `DEBUG` | Enable debug mode | `true` |
| `UPLOAD_DIR` | Directory for uploaded files | `./uploads` |
| `CLONE_DIR` | Directory for cloned repos | `./cloned_repos` |
| `REPORTS_DIR` | Directory for generated reports | `./reports` |
| `MAX_FILE_SIZE_MB` | Maximum upload file size | `100` |

## Target Use Cases

- **Code Onboarding**: Help new developers understand codebases quickly
- **Code Reviews**: Accelerate code review and audit processes
- **Knowledge Transfer**: Facilitate knowledge sharing between teams
- **Open Source Understanding**: Quickly grasp open-source project structures
- **Legacy Documentation**: Generate documentation for legacy systems

## License

MIT License - feel free to use this project for any purpose.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
