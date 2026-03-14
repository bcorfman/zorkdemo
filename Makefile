PACKAGE := zorkdemo
PACKAGE_DIR := .
.SILENT: setup install devinstall test run lint format all ensure-backend

PYTHON_VERSION ?= 3.12
BACKEND_HOST ?= 127.0.0.1
BACKEND_PORT ?= 8000
FRONTEND_HOST ?= 127.0.0.1
FRONTEND_PORT ?= 5173
BACKEND_URL ?= http://$(BACKEND_HOST):$(BACKEND_PORT)
FRONTEND_URL ?= http://$(FRONTEND_HOST):$(FRONTEND_PORT)
DATABASE_URL ?= sqlite:///sessions.db
CORS_ALLOW_ORIGINS ?= http://localhost:5173,http://127.0.0.1:5173
BACKEND_LOG ?= .tmp/zorkdemo-backend.log

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
	uv run python -m backend.app.dev_runner ensure-backend \
		--backend-url "$(BACKEND_URL)" \
		--backend-host "$(BACKEND_HOST)" \
		--backend-port "$(BACKEND_PORT)" \
		--database-url "$(DATABASE_URL)" \
		--cors-allow-origins "$(CORS_ALLOW_ORIGINS)" \
		--backend-log "$(BACKEND_LOG)"

run: ensure-backend
	uv run python -m backend.app.dev_runner open-browser --frontend-url "$(FRONTEND_URL)"
	uv run python -m backend.app.dev_runner run-frontend \
		--frontend-dir frontend \
		--api-base-url "$(BACKEND_URL)" \
		--frontend-host "$(FRONTEND_HOST)" \
		--frontend-port "$(FRONTEND_PORT)"

lint:
	uv run ruff check .

format:
	uv run ruff format .

all: devinstall lint format test
