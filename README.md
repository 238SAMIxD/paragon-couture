# Paragon Couture - AI Agent PoC

A modern Proof of Concept (PoC) demonstrating a microservice architecture designed for AI agent integration. This project emphasizes robust observability, clean API design, and a scalable frontend client, aligning with modern MLOps and backend engineering standards.

## ⚠️ Project Scope & UI Disclaimer

This repository is currently under active development. The primary focus of this PoC is the backend architecture, observability infrastructure (OpenTelemetry), and the upcoming Model Context Protocol (MCP) integration for LLMs.

The included React application serves as a Minimum Viable Product (MVP) client to validate the End-to-End flow and API communication. It is not intended to represent a fully polished, production-ready user interface at this stage.

## 🏗️ Architecture & Tech Stack

### Backend

The microservice is built for high performance and tracing capabilities:

- **Framework:** Python with FastAPI for asynchronous REST endpoints.
- **Observability:** Native OpenTelemetry integration (`telemetry.py`) for detailed request tracing and LLM generation monitoring.
- **Data Validation:** Pydantic models for strict payload validation.
- **Database:** Core database integration prepared via `database.py` and `database_models.py`.

### Frontend

A strictly typed, component-based client application:

- **Core:** React with TypeScript, powered by Vite.
- **Architecture:** Atomic design pattern implementations (Atoms, Molecules, Organisms).
- **Testing:** E2E testing configured with Playwright (`paragon-flow.spec.ts`).

### Infrastructure & Tooling

- **Containerization:** `docker-compose.yml` for unified local development environments.
- **Task Runner:** `justfile` included for streamlined command execution and environment setup.
- **Dependency Management:** `uv.lock` and `pyproject.toml` for the backend, `pnpm` for the frontend.

## 🗺️ Roadmap / Work in Progress

- [x] **Phase 1: Foundation**
  - Setup FastAPI backend with custom middleware.
  - Initialize React/TypeScript frontend with Vite.
  - Configure local Docker ecosystem.
- [x] **Phase 2: Observability & Core Logic**
  - Implement OpenTelemetry tracing for API routes.
  - Setup database models and core logger.
  - Implement E2E testing foundation with Playwright.
- [x] **Phase 3: AI Integration (Current)**
  - Integrate Gemini LLM engine.
  - Implement Model Context Protocol (MCP) for tool execution.
  - Expose agent capabilities via REST endpoints.

## 🚀 Getting Started

### Prerequisites

- Docker & Docker Compose
- Node.js & pnpm
- Python 3.12+
- `just` command runner

### Running Locally

We use [`just`](https://just.systems/) to streamline the development workflow and manage commands.

1. **Clone the repository:**

```bash
git clone <repository-url>
cd paragon-couture
```

2. **Install all dependencies** (Frontend `pnpm`, Backend `uv`):

```bash
just setup
```

3. **Start the comprehensive local development environment** (starts Docker containers, runs backend, runs frontend):

```bash
just dev
```

Alternatively, you can run individual services:

- **Database/Infrastructure:** `just db-up`
- **Frontend development server:** `just dev-frontend`
- **Backend development server:** `just dev-backend`

### 🔬 Observability (OpenTelemetry & Jaeger)

The backend is fully instrumented with **OpenTelemetry**. When running the infrastructure via Docker Compose (`just dev` or `just db-up`), a Jaeger container is automatically started to collect and visualize traces.

- **Jaeger UI:** Access the tracing dashboard at [http://localhost:16686](http://localhost:16686) to inspect API requests, LLM generation flows, and database queries.

## 🧪 Testing

The project includes foundational tests for both stacks that can be executed easily using `just`:

- **All Tests:** Run `just test` to execute both backend and frontend tests.
- **Backend:** Run `just test-backend` to execute pytest tests.
- **Frontend (Headless):** Run `just test-frontend` to execute Playwright E2E flows.
- **Frontend (UI Mode):** Run `just test-frontend-ui` to open the Playwright UI.
