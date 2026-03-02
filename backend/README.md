# Backend (Phase 0 Scaffold)

This directory is reserved for the FastAPI backend service that will run on Railway.

## Status

Phase 0 scaffold only. The production backend logic is still in the legacy `web/` package until Phase 1 migration is complete.

## Environment Variables (Standardized)

- `DATABASE_URL`: Postgres connection string for session persistence.
- `CORS_ALLOW_ORIGINS`: Comma-separated allowed origins (for example, GitHub Pages URL + localhost).

## Planned Run Command (Phase 1+)

```sh
uv run uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
