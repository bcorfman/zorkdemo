# zorkdemo

[![Python build and test](https://github.com/bcorfman/zorkdemo/actions/workflows/build-test.yml/badge.svg)](https://github.com/bcorfman/zorkdemo/actions/workflows/build-test.yml)

#### 🌏  Open in the Cloud 

Click any of the buttons below to start a new development environment to demo or contribute to the codebase without having to install anything on your machine:

[![Open in VS Code](https://img.shields.io/badge/Open%20in-VS%20Code-blue?logo=visualstudiocode)](https://vscode.dev/github/bcorfman/zorkdemo)
[![Open in Glitch](https://img.shields.io/badge/Open%20in-Glitch-blue?logo=glitch)](https://glitch.com/edit/#!/import/github/bcorfman/zorkdemo)
[![Open in Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=338102781&machine=standardLinux32gb&devcontainer_path=.devcontainer%2Fdevcontainer.json&location=EastUs)
[![Open in StackBlitz](https://developer.stackblitz.com/img/open_in_stackblitz.svg)](https://stackblitz.com/github/bcorfman/zorkdemo)
[![Edit in Codesandbox](https://codesandbox.io/static/img/play-codesandbox.svg)](https://codesandbox.io/s/github/bcorfman/zorkdemo)
[![Open in Repl.it](https://replit.com/badge/github/withastro/astro)](https://replit.com/github/bcorfman/zorkdemo)
[![Open in Codeanywhere](https://codeanywhere.com/img/open-in-codeanywhere-btn.svg)](https://app.codeanywhere.com/#https://github.com/bcorfman/zorkdemo)
[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/bcorfman/zorkdemo)

Runs on Linux, Windows or Mac.

A (much simplified) port of a famous adventure game to help teach my daughter how to program in Python.

Two easy ways to launch the console project:

1. Click on the Open with GitHub Codespaces badge above to launch the project in a browser or on your desktop inside Visual Studio Code, then type `uv run python zorkdemo.py` in the terminal window.
2. Download one of the binary releases and run the file on your system.

NOTE: the MacOS version does not have code signing built into it yet (that's next on my list!). To run it, you will need to set the binary as executable with `chmod 755` or similar, and after trying to run it once, go through System Preferences: Security and Privacy: General and "Allow the program to run anyway".

## Monorepo Layout (Phase 0)

- `adventure/`: shared game engine logic
- `backend/`: FastAPI service (SQLAlchemy + Alembic, target Railway deploy)
- `frontend/`: TypeScript frontend app (target GitHub Pages deploy)
- `web/`: current legacy Hug web app
- `docs/architecture.md`: migration architecture notes

## Local Development Quickstart

Install tooling and Python dependencies:

- Install [Python](https://www.python.org) 3.10+
- Install [uv](https://docs.astral.sh/uv/)
- Run `uv sync --all-groups` from repo root

Standardized environment variables:

- Backend: `DATABASE_URL`, `CORS_ALLOW_ORIGINS` (see `backend/.env.example`)
- Frontend: `VITE_API_BASE_URL` (see `frontend/.env.example`)

## Makefile Workflow

Key targets:

- `make setup`: install project tooling (`uv`, and Node/npm if missing)
- `make install`: install runtime dependencies only
- `make devinstall`: install full dev/test dependencies
- `make lint`: run `ruff check`
- `make format`: run `ruff format`
- `make test`: run Python + frontend tests
- `make run`: ensure local backend is up, launch frontend dev server, and open browser (Linux/macOS/Windows)

`make run` uses `uv run python -m backend.app.dev_runner` for cross-platform process startup, health checks, and browser opening.

Optional `make run` variables:

- `BACKEND_HOST`, `BACKEND_PORT`, `FRONTEND_HOST`, `FRONTEND_PORT`
- `DATABASE_URL`, `CORS_ALLOW_ORIGINS`
- `BACKEND_LOG` (default: `.tmp/zorkdemo-backend.log`)

## Deployment (Phase 4)

### Frontend (GitHub Pages)

- Workflow: [.github/workflows/deploy-frontend-pages.yml](/home/bcorfman/dev/zorkdemo/.github/workflows/deploy-frontend-pages.yml)
- Set repository variable `VITE_API_BASE_URL` to your Railway backend URL (example: `https://<service>.up.railway.app`).
- Push to `main` to build and publish `frontend/dist`.

### Backend (Railway)

- Deployment config: [railway.toml](/home/bcorfman/dev/zorkdemo/railway.toml)
- Health endpoint used by deployment config: `/api/v1/health`
- Required Railway env vars:
  - `DATABASE_URL` (from Railway Postgres plugin)
  - `CORS_ALLOW_ORIGINS` (must include your GitHub Pages URL)
- Optional GitHub Actions deploy workflow: [.github/workflows/deploy-backend-railway.yml](/home/bcorfman/dev/zorkdemo/.github/workflows/deploy-backend-railway.yml)
  - Requires secret `RAILWAY_TOKEN`
  - Requires repo variable `RAILWAY_SERVICE`
  - Optional repo variable `BACKEND_HEALTHCHECK_URL`

## Extending The Game

For adding new locations, items, and commands, see:

- [docs/extending-game.md](/home/bcorfman/dev/zorkdemo/docs/extending-game.md)

### Run Backend (FastAPI v1 API)

```sh
uv run alembic -c backend/alembic.ini upgrade head
uv run uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

API endpoints:

- `GET /api/v1/health`
- `POST /api/v1/session`
- `POST /api/v1/command`
- `POST /api/v1/session/reset`

### Run Backend (Legacy Hug App)

```sh
uv run hug -m web.app
```

Navigate to [http://localhost:8000/](http://localhost:8000/)

### Run Frontend (TypeScript App)

```sh
cd frontend
npm install
npm run dev
```

Navigate to [http://localhost:5173/](http://localhost:5173/)