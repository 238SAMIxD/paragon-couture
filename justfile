set shell := ["bash", "-c"]

@frontend-dev:
    cd frontend && pnpm run dev

@backend-dev:
    cd backend && uv run uvicorn main:app --reload --port 8000
