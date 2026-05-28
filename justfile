set shell := ["bash", "-c"]

# Setup scripts

@setup-frontend:
    cd frontend && pnpm i

@setup-backend:
    cd backend && uv sync

@setup:
    just setup-frontend && just setup-backend

# Dev scripts

@db-up:
    docker-compose up -d

@db-down:
    docker-compose down

@db-restart:
    docker-compose restart

@dev-frontend:
    cd frontend && pnpm run dev

@dev-backend:
    cd backend && uv run uvicorn main:app --reload --port 8000

@dev:
    just db-up & just dev-frontend & just dev-backend & wait

# Test scripts

@test-backend:
    cd backend && uv run python -m pytest tests/ -v

@test-frontend:
    cd frontend && pnpm exec playwright test

@test-frontend-ui:
    cd frontend && pnpm exec playwright test --ui

@test:
    just test-backend && just test-frontend
