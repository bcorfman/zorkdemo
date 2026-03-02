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
- `frontend/`: TypeScript frontend scaffold (target GitHub Pages deploy)
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

### Run Frontend (Phase 0 Placeholder)

```sh
cd frontend
uv run python -m http.server 5173
```

Navigate to [http://localhost:5173/](http://localhost:5173/)

## Legacy Hug Notes

The easiest option is to create a `.env` file in the root of the project with the contents:

```config
SECRET_KEY="<some random key>"
```

Alternatively, you can manually set your environment variables for your terminal session, but you'll have to remember to do that for every new session.

```sh
export SECRET_KEY="<put something random here>"
```

### Running the legacy development web server

In the root of the project, run:

```sh
uv run hug -m web.app
```

Navigate in your browser to:

[http://localhost:8000/](http://localhost:8000/)

Have fun!

If you want to restart delete your `sid` cookie from your browser and refresh the page.

**NOTE:** future versions should provide a link to an endpoint to achieve something like this.

Or, you could delete your session record from the Sqlite database.

## Web TODO Items

- make endsession actually work
- provide link to endsession
- alignment between input and output for seamless experience
- figure out how to handle quit/exit
- wsgi file for hooking this up to a real web server and hosting
