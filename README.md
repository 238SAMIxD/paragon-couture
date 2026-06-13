# 🎈 Paragon Couture - Enterprise AI Fashion Dashboard
## 📖 Overview
Paragon Couture is a full-stack, cloud-native web application that generates luxury *haute couture* fashion designs specifically for monkeys in the Bloons TD 6 (BTD6) universe. Built with an enterprise-grade architecture, the system leverages local Large Language Models (Ollama) for structured text generation and local Diffusion models (via ComfyUI) for high-end image rendering.
## 🚀 Tech Stack
### Frontend (User Interface)
 * **Framework:** React 19 + TypeScript
 * **Build Tool:** Vite
 * **Styling:** Tailwind CSS 4 (Custom "Fancy BTD6" Glassmorphism theme)
 * **Testing:** Playwright (End-to-End E2E)
 * **State & Routing:** React Hooks, React Router DOM v7
 * **Tooling:** ESLint, Prettier, Just
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
   * Zero data leaves the host machine. Text generation is handled by Ollama, prompting strict JSON schemas enforced by Pydantic. Image generation is offloaded to a local ComfyUI instance, optimized for modern hardware (e.g., AMD Strix Halo).
 2. **Cloud-Native Observability:**
   * Custom ASGI middleware generates unique request_ids. All logs are output in structured JSON format via structlog, perfectly formatted for ingestion by GCP Cloud Logging, Azure Application Insights, or Datadog.
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
│   └── pyproject.toml       # Python dependencies (uv)
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
 * **Python 3.12+ & uv** (Backend package manager)
 * **Docker** (For PostgreSQL)
 * **Ollama** (Running locally with llama3.1 model)
 * **ComfyUI** (Running locally on default port 8188 with SDXL Turbo/equivalent models)
### Development Commands
We use just as our command runner for a seamless Developer Experience (DX).
**1. Infrastructure & Install**
```bash
# Start PostgreSQL via Docker
docker compose up -d

# Install all dependencies (Frontend + Backend)
just setup

```
**2. Run the Application**
```bash
# Start both FastAPI backend and React frontend
just dev

```
 * Frontend will be available at: http://localhost:5173
 * Backend API Docs (Swagger) at: http://localhost:8000/docs
**3. Quality Assurance & Testing**
```bash
# Run strict formatters and linters (ESLint, Prettier, Ruff, Mypy)
just audit

# Run Backend Integration Tests
just test-backend

# Run Frontend E2E Tests (Playwright UI Mode)
just test-frontend-ui

```

