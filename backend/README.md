# Backend

This directory contains the FastAPI backend service that will run on Railway.

## Status

Phase 2 complete. Session persistence now uses SQLAlchemy with Alembic migrations.

## Environment Variables (Standardized)

- `DATABASE_URL`: Postgres connection string for session persistence.
- `CORS_ALLOW_ORIGINS`: Comma-separated allowed origins (for example, GitHub Pages URL + localhost).
- `STORY_FILE` (optional): absolute/relative path to a `.z3` story file. If missing or invalid, the backend falls back to `data/zork1.z3`.

## Run Command

```sh
uv run uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Database Migrations

```sh
uv run alembic -c backend/alembic.ini upgrade head
```

## Railway Deployment

- Railway config file: `railway.toml`
- Health check path: `/api/v1/health`
- Required env vars:
  - `DATABASE_URL`
  - `CORS_ALLOW_ORIGINS` (include `https://bcorfman.github.io` for production frontend)
- Optional env vars:
  - `STORY_FILE` (custom Z-machine story path; invalid values fall back to bundled `data/zork1.z3`)

## API Endpoints

- `GET /api/v1/health`
- `POST /api/v1/session`
- `POST /api/v1/command`
- `POST /api/v1/session/reset`
