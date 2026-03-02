# Contributing

## Development Workflow (Phase 0)

This repository is in a staged migration from Hug to FastAPI + TypeScript frontend.

### Prerequisites

- Python 3.10+
- `uv`
- Node.js 20+ (for frontend phase)

### Install Python dependencies

```sh
uv sync --all-groups
```

### FastAPI backend (Phase 1)

```sh
uv run uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Current runnable app (legacy Hug)

```sh
uv run hug -m web.app
```

### New app directories

- `backend/`: FastAPI service scaffold (implementation begins in Phase 1).
- `frontend/`: TypeScript frontend scaffold (implementation begins in Phase 3).

## Environment Setup

Copy and adjust env templates as needed:

- `backend/.env.example`
- `frontend/.env.example`

## Testing

Current tests:

```sh
uv run pytest
```
