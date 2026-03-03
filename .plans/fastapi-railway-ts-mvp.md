# [ ] MVP Migration Plan: FastAPI on Railway + TypeScript Frontend on GitHub Pages

## [ ] Summary
- [ ] Build FastAPI backend on Railway using existing Python game logic
- [ ] Build React + TypeScript frontend on GitHub Pages
- [ ] Persist anonymous sessions in Railway Postgres via browser-stored UUID

## [ ] Architecture Decisions (Locked)
- [ ] Frontend stack: `Vite + React + TypeScript`
- [ ] Session model: anonymous UUID stored in browser `localStorage`
- [ ] Session persistence: Railway Postgres
- [ ] API transition: clean API now under `/api/v1/*` (no Hug compatibility paths)

## [ ] Public API / Interface Changes

### [ ] Backend HTTP API (new)
- [ ] `GET /api/v1/health` -> `{ "status": "ok" }`
- [ ] `POST /api/v1/session` -> create/validate session
- [ ] `POST /api/v1/command` -> execute command and persist state
- [ ] `POST /api/v1/session/reset` -> clear state for session

### [ ] TypeScript Frontend Types (new)
- [ ] `SessionCreateRequest`, `SessionCreateResponse`
- [ ] `CommandRequest`, `CommandResponse`
- [ ] `ApiError` with stable `code` + `message`
- [ ] Runtime API response validation (e.g. Zod)

### [ ] Persistence Contract
- [ ] Create `adventure_sessions` table
- [ ] Fields: `session_id`, `save_data`, `created_at`, `updated_at`

## [x] Phase 0: Repo Restructure + Guardrails (Day 1)
- [x] Create `backend/` and `frontend/` directories
- [x] Keep `adventure/` reusable by backend
- [x] Add architecture + local dev quickstart docs
- [x] Standardize env vars (`DATABASE_URL`, `CORS_ALLOW_ORIGINS`, `VITE_API_BASE_URL`)
- [x] Add `CONTRIBUTING.md` for backend/frontend workflows

### [x] Exit Criteria
- [x] Monorepo layout documented
- [x] README has exact run instructions for both apps

## [x] Phase 1: FastAPI Adapter over Existing Engine (Day 1-2)
- [x] Create FastAPI app with startup DB init + CORS + Pydantic models
- [x] Implement service flow: load session -> optional `admin_load` -> execute -> `admin_save`
- [x] Implement `/health`, `/session`, `/command`, `/session/reset`
- [x] Preserve current markdown-to-HTML response behavior

### [x] Exit Criteria
- [x] Manual API flow works end-to-end
- [x] Command response parity with current Hug behavior

## [x] Phase 2: Postgres Persistence (Day 2)
- [x] Add SQLAlchemy 2.0 + Alembic in backend
- [x] Create initial migration for `adventure_sessions`
- [x] Add `SessionRepository` abstraction
- [x] Implement `PostgresSessionRepository`
- [x] Ensure idempotent session create/get semantics

### [x] Exit Criteria
- [x] Fresh DB migration succeeds
- [x] Save/load survives app restart
- [x] Reset endpoint clears state correctly

## [x] Phase 3: TS Frontend MVP (Day 2-3)
- [x] Create React UI: transcript, input, status/error, reset/new game
- [x] Implement session bootstrap from `localStorage`
- [x] Implement command send/receive flow with loading states
- [x] Configure `VITE_API_BASE_URL` for environment-specific backend URL
- [x] Ensure production build works for GitHub Pages

### [x] Exit Criteria
- [x] App playable from GitHub Pages
- [x] Refresh resumes session
- [x] Reset starts a fresh session

## [ ] Phase 4: Deployments + CI/CD (Day 3-4)
- [ ] Deploy backend service to Railway
- [ ] Attach Railway Postgres plugin
- [x] Configure backend env vars and health check
- [x] Configure GitHub Action to build/deploy frontend to Pages
- [x] Configure production CORS for GitHub Pages origin(s)

### [ ] Exit Criteria
- [ ] Railway API healthy
- [ ] GitHub Pages deployed successfully
- [ ] Frontend can call production API without CORS errors

## [ ] Phase 5: Quality, Tests, Contributor UX (Day 4-5)
- [ ] Backend route tests (`health/session/command/reset`)
- [ ] Backend service + persistence tests
- [ ] Frontend API + UI behavior tests
- [ ] End-to-end smoke test for play/resume/reset
- [ ] Add contributor docs for extending content and commands

### [ ] Exit Criteria
- [ ] CI green for backend + frontend
- [ ] New contributor can run project in <10 minutes from docs

## [ ] Data-Driven Expandability (MVP-Compatible Staging)
- [ ] Keep existing Python engine for MVP
- [ ] Define `content/` contract for locations/items/commands metadata
- [ ] Keep parser/engine in code for now
- [ ] Plan post-MVP migration of content into validated data files
- [ ] Add command registry pattern for future plugin-style expansion

## [ ] Testing Scenarios and Acceptance Criteria

### [ ] Core gameplay/session
- [ ] New browser session starts correctly
- [ ] Command execution returns expected HTML output
- [ ] Refresh resumes session state
- [ ] Reset clears state
- [ ] Invalid/empty input returns stable error

### [ ] Reliability
- [ ] Session survives backend restart
- [ ] Unknown `session_id` handled by create-on-demand policy
- [ ] DB outage returns structured 5xx response

### [ ] Deployment
- [ ] GitHub Pages deploy on main succeeds
- [ ] Railway deploy succeeds and health check passes
- [ ] Production supports multi-command gameplay flow

## [ ] Risks and Mitigations
- [ ] Session schema drift -> add session versioning + migrations
- [ ] Markdown rendering drift -> snapshot parity tests
- [ ] CORS issues -> explicit allowed-origins env + integration check

## [ ] Assumptions and Defaults
- [ ] No auth/login in MVP
- [ ] One local session token per browser
- [ ] Backend is API-only (no server-rendered pages)
- [ ] Python engine retained for MVP timeline
- [ ] Postgres is source of truth for saves
- [ ] Full data-driven engine evolution happens post-MVP
