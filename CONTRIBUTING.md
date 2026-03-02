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
