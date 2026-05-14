set shell := ["bash", "-c"]

@dev-frontend:
    cd frontend && pnpm run dev

@dev-backend:
    cd backend && uv run uvicorn main:app --reload --port 8000

@setup-frontend:
    cd frontend && pnpm i

@setup-backend:
    cd backend && uv sync

@setup:
    just setup-frontend && just setup-backend

@dev:
    just dev-frontend & just dev-backend & wait
