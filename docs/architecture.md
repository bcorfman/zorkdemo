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
- Backend persists session save blobs in Postgres.

## Environment Variables

### Backend

- `DATABASE_URL`
- `CORS_ALLOW_ORIGINS`

### Frontend

- `VITE_API_BASE_URL`
