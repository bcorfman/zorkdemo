# Contributing

## Development Workflow

This repository is in a staged migration from Hug to FastAPI + TypeScript frontend.

### Prerequisites

- Python 3.10+
- `uv`
- Node.js 20+ (for frontend phase)

### Install Python dependencies

```sh
uv sync --all-groups
```

### FastAPI backend

```sh
uv run uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Run DB migrations

```sh
uv run alembic -c backend/alembic.ini upgrade head
```

### Deployment variables

- GitHub Pages frontend build: `VITE_API_BASE_URL` (repository variable)
- Railway backend deploy workflow:
  - secret: `RAILWAY_TOKEN`
  - variables: `RAILWAY_SERVICE`, optional `BACKEND_HEALTHCHECK_URL`

### Current runnable app (legacy Hug)

```sh
uv run hug -m web.app
```

### Frontend (Phase 3)

```sh
cd frontend
npm install
npm run dev
npm run test
```

### New app directories

- `backend/`: FastAPI service with SQLAlchemy + Alembic persistence.
- `frontend/`: React + TypeScript app (Vite).

## Environment Setup

Copy and adjust env templates as needed:

- `backend/.env.example`
- `frontend/.env.example`

## Testing

Current tests:

```sh
uv run pytest
```

## Contributor Quickstart (Under 10 Minutes)

1. `make setup`
2. `make devinstall`
3. `uv run alembic -c backend/alembic.ini upgrade head`
4. `make run`
5. In a second terminal, run `make test`

## Extending Commands And Content

See [docs/extending-game.md](/home/bcorfman/dev/zorkdemo/docs/extending-game.md) for:

- adding new locations and items
- registering new commands in `adventure/app.py`
- updating tests for game and API behavior
