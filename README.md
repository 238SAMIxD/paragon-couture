# Paragon Couture - AI Agent PoC

A modern Proof of Concept (PoC) demonstrating a microservice architecture designed for AI agent integration. This project emphasizes robust observability, clean API design, and a scalable frontend client, aligning with modern MLOps and backend engineering standards.

## ⚠️ Project Scope & UI Disclaimer

This repository is currently under active development. The primary focus of this PoC is the backend architecture, observability infrastructure (OpenTelemetry), and the upcoming Model Context Protocol (MCP) integration for LLMs.

The included React application serves as a Minimum Viable Product (MVP) client to validate the End-to-End flow and API communication. It is not intended to represent a fully polished, production-ready user interface at this stage.

## 🏗️ Architecture & Tech Stack

### Backend

The microservice is built for high performance and tracing capabilities:

- **Framework:** Python with FastAPI for asynchronous REST endpoints[cite: 3].
- **Observability:** Native OpenTelemetry integration (`telemetry.py`) for detailed request tracing and LLM generation monitoring[cite: 3].
- **Data Validation:** Pydantic models for strict payload validation.
- **Database:** Core database integration prepared via `database.py` and `database_models.py`[cite: 3].

### Frontend

A strictly typed, component-based client application:

- **Core:** React with TypeScript, powered by Vite[cite: 3].
- **Architecture:** Atomic design pattern implementations (Atoms, Molecules, Organisms)[cite: 3].
- **Testing:** E2E testing configured with Playwright (`paragon-flow.spec.ts`)[cite: 3].

### Infrastructure & Tooling

- **Containerization:** `docker-compose.yml` for unified local development environments[cite: 3].
- **Task Runner:** `justfile` included for streamlined command execution and environment setup[cite: 3].
- **Dependency Management:** `uv.lock` and `pyproject.toml` for the backend, `pnpm` for the frontend[cite: 3].

## 🗺️ Roadmap / Work in Progress

- [x] **Phase 1: Foundation**
  - Setup FastAPI backend with custom middleware[cite: 3].
  - Initialize React/TypeScript frontend with Vite[cite: 3].
  - Configure local Docker ecosystem[cite: 3].
- [x] **Phase 2: Observability & Core Logic**
  - Implement OpenTelemetry tracing for API routes[cite: 3].
  - Setup database models and core logger[cite: 3].
  - Implement E2E testing foundation with Playwright[cite: 3].
- [ ] **Phase 3: AI Integration (Current)**
  - Integrate Gemini LLM engine.
  - Implement Model Context Protocol (MCP) for tool execution.
  - Expose agent capabilities via REST endpoints.

## 🚀 Getting Started

### Prerequisites

- Docker & Docker Compose
- Node.js & pnpm
- Python 3.12+[cite: 3]
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

## 🧪 Testing

The project includes foundational tests for both stacks that can be executed easily using `just`:

- **All Tests:** Run `just test` to execute both backend and frontend tests.
- **Backend:** Run `just test-backend` to execute pytest tests.
- **Frontend (Headless):** Run `just test-frontend` to execute Playwright E2E flows.
- **Frontend (UI Mode):** Run `just test-frontend-ui` to open the Playwright UI.
