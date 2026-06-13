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
    just db-up & just dev-backend & just dev-frontend & wait

# Test scripts

@test-backend:
    cd backend && uv run python -m pytest tests/ -v

@test-frontend:
    cd frontend && pnpm exec playwright test

@test-frontend-ui:
    cd frontend && pnpm exec playwright test --ui

@test:
    just test-backend && just test-frontend && just test-frontend-ui

# Quality scripts

@lint-frontend:
    cd frontend && pnpm run lint

@lint-backend:
    cd backend && uv run ruff check src/ main.py --line-length=100

@lint:
    just lint-frontend && just lint-backend

@format:
    cd frontend && pnpm run format

@format-check:
    cd frontend && pnpm run format:check

@fallow:
    cd frontend && npx fallow audit

@vulture:
    cd backend && uv run vulture src/ main.py --min-confidence 80 --exclude .venv,__pycache__,tests

@quality:
    just fallow && just vulture
