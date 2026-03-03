PACKAGE := zorkdemo
PACKAGE_DIR := .
SHELL := env PYTHON_VERSION=3.10 /bin/bash
.SILENT: setup install devinstall test run lint format all ensure-backend

PYTHON_VERSION ?= 3.10
BACKEND_HOST ?= 127.0.0.1
BACKEND_PORT ?= 8000
FRONTEND_HOST ?= 127.0.0.1
FRONTEND_PORT ?= 5173
BACKEND_URL ?= http://$(BACKEND_HOST):$(BACKEND_PORT)
FRONTEND_URL ?= http://$(FRONTEND_HOST):$(FRONTEND_PORT)
DATABASE_URL ?= sqlite:///sessions.db
CORS_ALLOW_ORIGINS ?= http://localhost:5173,http://127.0.0.1:5173

setup:
	if ! command -v uv >/dev/null 2>&1; then \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	fi
	if ! command -v npm >/dev/null 2>&1; then \
		echo "npm not found; installing Node.js LTS via nvm"; \
		export NVM_DIR="$$HOME/.nvm"; \
		if [ ! -s "$$NVM_DIR/nvm.sh" ]; then \
			curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash; \
		fi; \
		. "$$NVM_DIR/nvm.sh"; \
		nvm install --lts; \
	fi

install:
	uv python pin $(PYTHON_VERSION)
	uv sync --no-dev
	cd frontend && npm install --omit=dev

devinstall:
	uv python pin $(PYTHON_VERSION)
	uv sync --all-groups
	cd frontend && npm install

test:
	uv run pytest
	cd frontend && npm run test

ensure-backend:
	if ! curl -fsS "$(BACKEND_URL)/api/v1/health" >/dev/null 2>&1; then \
		echo "Starting backend at $(BACKEND_URL)"; \
		DATABASE_URL="$(DATABASE_URL)" CORS_ALLOW_ORIGINS="$(CORS_ALLOW_ORIGINS)" uv run alembic -c backend/alembic.ini upgrade head; \
		DATABASE_URL="$(DATABASE_URL)" CORS_ALLOW_ORIGINS="$(CORS_ALLOW_ORIGINS)" uv run uvicorn backend.app.main:app --host $(BACKEND_HOST) --port $(BACKEND_PORT) > /tmp/zorkdemo-backend.log 2>&1 & \
		sleep 2; \
	fi
	if ! curl -fsS "$(BACKEND_URL)/api/v1/health" >/dev/null 2>&1; then \
		echo "Backend failed to start. See /tmp/zorkdemo-backend.log"; \
		exit 1; \
	fi

run: ensure-backend
	if command -v xdg-open >/dev/null 2>&1; then \
		xdg-open "$(FRONTEND_URL)" >/dev/null 2>&1 & \
	elif command -v wslview >/dev/null 2>&1; then \
		wslview "$(FRONTEND_URL)" >/dev/null 2>&1 & \
	elif command -v open >/dev/null 2>&1; then \
		open "$(FRONTEND_URL)" >/dev/null 2>&1 & \
	else \
		echo "Open $(FRONTEND_URL) in your browser."; \
	fi
	cd frontend && VITE_API_BASE_URL="$(BACKEND_URL)" npm run dev -- --host $(FRONTEND_HOST) --port $(FRONTEND_PORT)

lint:
	uv run ruff check .

format:
	uv run ruff format .

all: devinstall lint format test
