# Backend (Phase 0 Scaffold)

This directory is reserved for the FastAPI backend service that will run on Railway.

## Status

Phase 1 complete. FastAPI v1 endpoints are available in `backend.app.main`.

## Environment Variables (Standardized)

- `DATABASE_URL`: Postgres connection string for session persistence.
- `CORS_ALLOW_ORIGINS`: Comma-separated allowed origins (for example, GitHub Pages URL + localhost).

## Run Command

```sh
uv run uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

- `GET /api/v1/health`
- `POST /api/v1/session`
- `POST /api/v1/command`
- `POST /api/v1/session/reset`
