# 🎈 Paragon Couture - Enterprise AI Fashion Dashboard

## 📖 Overview
Paragon Couture is a full-stack, cloud-native web application that generates luxury *haute couture* fashion designs specifically for monkeys in the Bloons TD 6 (BTD6) universe. Built with an enterprise-grade developer experience focused on local/air-gapped AI inference and end-to-end testing.

## 🚀 Tech Stack
### Frontend (User Interface)
 * **Framework:** React 19 + TypeScript
 * **Build Tool:** Vite
 * **Styling:** Tailwind CSS 4 (Custom "Fancy BTD6" Glassmorphism theme)
 * **Testing:** Playwright (End-to-End E2E)
 * **State & Routing:** React Hooks, React Router DOM v7
 * **Tooling:** ESLint, Prettier, pnpm

### Backend (API & AI Pipeline)
 * **Framework:** FastAPI (Asynchronous)
 * **Language:** Python 3.12+
 * **Database:** PostgreSQL (running in Docker) via asyncpg and SQLAlchemy ORM
 * **AI Text Generation:** Local Ollama (llama3.1) configured via standard openai Python client for JSON structured outputs.
 * **AI Image Generation:** Local ComfyUI workflow integration (comfyui_service.py).
 * **Observability:** OpenTelemetry (Tracing) & Structlog (Structured JSON Logging).
 * **Testing:** pytest with pytest-asyncio and httpx (Mocked LLM & In-Memory SQLite overrides).

## 🏗️ Architecture & Key Features
 1. **100% Local AI Pipeline (Air-Gapped Ready):**
   * Zero data leaves the host machine. Text generation is handled by Ollama, prompting strict JSON schemas enforced by Pydantic. Image generation is offloaded to a local ComfyUI instance.
 2. **Cloud-Native Observability:**
   * Custom ASGI middleware generates unique request_ids. All logs are output in structured JSON format via structlog, suitable for ingestion by cloud log sinks.
 3. **Robust Data Persistence:**
   * Fully asynchronous SQLAlchemy 2.0 integration with a PostgreSQL database, storing complete fashion collections, AI prompts, and generated metadata.
 4. **Automated Quality Assurance:**
   * Comprehensive backend integration tests (pytest) utilizing dependency overrides to prevent actual LLM/DB calls during CI runs.
   * Visual frontend workflow validation using Playwright E2E tests.

## 📂 Project Structure
```text
paragon-couture/
├── backend/                  
│   ├── src/                 
│   │   ├── api/             # Routers and ASGI Middleware (Observability)
│   │   ├── core/            # DB setup, Logger, Telemetry, Config
│   │   ├── models/          # Pydantic Schemas & SQLAlchemy Models
│   │   └── services/        # llm_service.py, comfyui_service.py, image_service.py
│   ├── tests/               # Pytest suite (conftest.py, test_api_fixed.py)
│   ├── main.py              # FastAPI application entry point
│   └── pyproject.toml       # Python dependencies
├── frontend/                
│   ├── src/
│   │   ├── components/      # Atomic Design (atoms, molecules, organisms)
│   │   ├── services/        # coutureService.ts (API client)
│   │   └── App.tsx          # Root React component
│   ├── tests/e2e/           # Playwright E2E test specifications
│   └── playwright.config.ts # Playwright configuration
├── docker-compose.yml       # PostgreSQL database service
└── justfile                 # Unified task runner
```

## 🛠️ Quick Start & Setup
### Prerequisites
 * **Node.js & pnpm** (Frontend)
 * **Python 3.12+** (Backend)
 * **Docker** (For PostgreSQL)
 * **Ollama** (Running locally with llama3.1 model)
 * **ComfyUI** (Running locally on default port 8188 with SDXL Turbo/equivalent models)
 * **uv** (optional) — used by the project to run/manage backend commands (see note below)

### Development Commands
We use just as our command runner for a seamless Developer Experience (DX).

#### 1. Infrastructure & Install
```bash
# Start PostgreSQL via Docker
docker compose up -d

# Install all dependencies (Frontend + Backend)
just setup
```

#### 2. Environment files (required)
Copy example env files and edit the backend values before running:
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```
Required backend env variables (examples):
- DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/paragon
- FRONTEND_URL=http://localhost:5173
- CORS_ALLOW_ORIGINS=http://localhost:5173,http://localhost:3000
- OLLAMA_URL=http://localhost:11434
- COMFYUI_URL=http://localhost:8188

(Refer to backend/.env.example for the exact variable names. The backend defaults to FRONTEND_URL=http://localhost:5173; set FRONTEND_URL if you run your frontend on a nonstandard port.)

#### Note about uv
The backend justfile uses `uv` (a small runner used in this repository). If you don't have `uv` installed, you can install it with pipx or pip, or run the backend commands with plain python / uvicorn. Example:
```bash
# using uv (recommended if present)
cd backend && uv sync
# or with pip
cd backend && python -m pip install -r requirements.txt
```

#### 3. Run the Application
```bash
# Start both FastAPI backend and React frontend (dev mode)
just dev
```
- Frontend dev server: http://localhost:5173
- Backend API Docs (Swagger) at: http://localhost:8000/docs

#### 4. Quality Assurance & Testing
```bash
# Run strict formatters and linters (ESLint, Prettier, Ruff, Mypy)
just audit

# Run Backend Integration Tests
just test-backend

# Run Frontend E2E Tests (Playwright UI Mode)
just test-frontend-ui
```

## API Examples
Health checks:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/health/image
```
Generate couture (POST /api/generate):
```bash
curl -s -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"trend_description":"retro neon","monkey_tower_class":"primary","camo_detection":false,"lead_popping":false}'
```
Generate image directly (POST /api/image-generate):
```bash
curl -s -X POST http://localhost:8000/api/image-generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"a fashionable dart monkey wearing neon goggles","seed":42}'
```

## Troubleshooting
- Image service unreachable: check ComfyUI is running on the configured COMFYUI_URL and port (default http://localhost:8188). Use /health/image to verify.
- LLM failures: ensure Ollama is running and accessible at OLLAMA_URL and the configured model (llama3.1) is available.
- CORS issues: set CORS_ALLOW_ORIGINS in backend/.env to include the frontend origin (e.g., http://localhost:5173).
- Tests failing in CI: backend tests use dependency overrides to avoid calling real LLM or DB; review backend/tests/conftest.py for the override behavior.

## Contributing
Please add a CONTRIBUTING.md and LICENSE if you plan to accept external contributions. Small PRs that improve documentation, tests, and reproducibility are especially welcome.


---

