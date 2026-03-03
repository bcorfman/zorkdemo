# Architecture (MVP Target)

## Monorepo Layout

- `adventure/`: existing game engine logic (shared by backend during MVP).
- `backend/`: FastAPI service for API and session persistence.
- `frontend/`: TypeScript browser client (GitHub Pages).
- `web/`: legacy Hug implementation (to be retired after migration).
- `.plans/`: migration plans and checklists.

## Runtime Topology

- Frontend is static and served by GitHub Pages.
- Frontend calls backend HTTP API on Railway.
- Backend persists session save blobs in Postgres via SQLAlchemy repository.
- Schema migrations are managed with Alembic (`backend/alembic`).

## Deployment Topology (Phase 4)

- Frontend deploy workflow: `.github/workflows/deploy-frontend-pages.yml`
- Backend deploy workflow: `.github/workflows/deploy-backend-railway.yml`
- Railway service config: `railway.toml`
- Backend health check: `/api/v1/health`

## Backend API (Phase 1)

- `GET /api/v1/health`
- `POST /api/v1/session`
- `POST /api/v1/command`
- `POST /api/v1/session/reset`

## Environment Variables

### Backend

- `DATABASE_URL`
- `CORS_ALLOW_ORIGINS`

## Persistence Notes (Phase 2)

- Primary table: `adventure_sessions`
- Repository adapter: `PostgresSessionRepository`
- Migration command: `uv run alembic -c backend/alembic.ini upgrade head`

### Frontend

- `VITE_API_BASE_URL`
