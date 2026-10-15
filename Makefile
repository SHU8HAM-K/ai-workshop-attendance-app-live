.DEFAULT_GOAL := help
COMPOSE_DEV  := docker compose -f docker-compose.dev.yml
COMPOSE_PROD := docker compose -f docker-compose.prod.yml
BACKEND      := cd backend &&
FRONTEND     := cd frontend &&
PYTHON       ?= py -3.13
VENV_PYTHON  := .venv/Scripts/python.exe

# LocalStack credentials. Any non-empty pair works — LocalStack does not verify
# them; they exist because boto3 refuses to sign a request without credentials.
AWS_LOCAL_ENV := MYAPP_S3_BUCKET=myapp-local \
                 MYAPP_S3_ENDPOINT_URL=http://localstack:4566 \
                 MYAPP_S3_ACCESS_KEY=test \
                 MYAPP_S3_SECRET_KEY=test

.PHONY: help init venv run-dev dev dev-down up down logs ps shell \
        install test test-be test-fe lint format check migrate migration \
        up-aws clean bench sizes review

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

# ── first run ────────────────────────────────────────────────────────────────
# >>> template-init (this block removes itself once `make init` has run)
init: ## Rename the template for a new app: make init NAME=orders
	@test -n "$(NAME)" || (echo "usage: make init NAME=your_app_name" && exit 1)
	@python3 scripts/init_project.py $(NAME)
# <<< template-init

install: ## Install backend + frontend dependencies locally (no docker)
	$(BACKEND) uv sync --all-groups
	$(FRONTEND) npm install

venv: ## Create .venv and install backend + frontend dependencies (Windows Git Bash)
	$(PYTHON) -m venv .venv
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install --editable ./backend
	$(FRONTEND) npm install
	@test -f .env || cp .env.example .env
	@echo "Setup complete. Run: make run-dev"

run-dev: ## Run FastAPI :8000 and Vite :5173 locally (no Docker)
	@test -x "$(VENV_PYTHON)" || (echo "Virtual environment missing. Run: make venv" && exit 1)
	@command -v npm >/dev/null || (echo "npm is required but was not found" && exit 1)
	@set -a; \
	  if [ -f .env ]; then . ./.env; fi; \
	  set +a; \
	  (cd backend && ../$(VENV_PYTHON) -m alembic upgrade head) || exit 1; \
	  (cd backend && ../$(VENV_PYTHON) -m uvicorn myapp.main:app --host 127.0.0.1 --port 8000 --reload) & \
	  backend_pid=$$!; \
	  (cd frontend && npm run dev) & \
	  frontend_pid=$$!; \
	  cleanup() { \
	    taskkill.exe //PID $$backend_pid //T //F >/dev/null 2>&1 || kill $$backend_pid 2>/dev/null || true; \
	    taskkill.exe //PID $$frontend_pid //T //F >/dev/null 2>&1 || kill $$frontend_pid 2>/dev/null || true; \
	  }; \
	  trap cleanup EXIT INT TERM; \
	  echo "FastAPI: http://localhost:8000"; \
	  echo "Browser: http://localhost:5173"; \
	  wait $$frontend_pid

# ── docker: development ──────────────────────────────────────────────────────
dev: ## Dev stack: Vite HMR :5173, API :8000, debugpy :5678
	$(COMPOSE_DEV) up --build

up-aws: ## Dev stack + LocalStack (S3/SQS/SNS/Secrets Manager) on :4566
	$(AWS_LOCAL_ENV) $(COMPOSE_DEV) --profile aws up --build

dev-down: ## Stop the dev stack
	$(COMPOSE_DEV) down

logs: ## Tail dev logs
	$(COMPOSE_DEV) logs -f

ps: ## Show running containers
	$(COMPOSE_DEV) ps

shell: ## Shell into the backend container
	$(COMPOSE_DEV) exec backend bash

# ── docker: production shape ─────────────────────────────────────────────────
up: ## Production image locally — SPA served by FastAPI on :8000
	$(COMPOSE_PROD) up --build

down: ## Stop the production stack
	$(COMPOSE_PROD) down

# ── database ─────────────────────────────────────────────────────────────────
migrate: ## Apply migrations to the dev database
	$(COMPOSE_DEV) exec backend alembic upgrade head

migration: ## Autogenerate a migration: make migration m="add orders table"
	@test -n "$(m)" || (echo 'usage: make migration m="what changed"' && exit 1)
	$(COMPOSE_DEV) exec backend alembic revision --autogenerate -m "$(m)"
	@echo "\n⚠  Read the generated file before committing. Autogenerate misses"
	@echo "   renames (it writes drop+add, which loses the data) and never"
	@echo "   writes a backfill."

# ── quality gates (run locally, same commands run in CI) ─────────────────────
check: lint test ## Everything CI runs

test: test-be test-fe ## Run all tests

test-be: ## Backend tests with coverage
	$(BACKEND) uv run pytest

test-fe: ## Frontend tests
	$(FRONTEND) npm run test

lint: ## Lint + typecheck both sides, dependency rule, file length
	$(BACKEND) uv run ruff check src tests
	$(BACKEND) uv run ruff format --check src tests
	$(BACKEND) uv run mypy src
	$(FRONTEND) npx tsc -b --noEmit
	@python3 scripts/check_dependency_rule.py
	@python3 scripts/check_file_length.py

bench: ## Run the micro-benchmarks with timing (normally they run untimed)
	$(BACKEND) uv run pytest tests/benchmark --benchmark-enable --benchmark-only --no-cov

sizes: ## List the largest files by code lines
	@python3 scripts/check_file_length.py --list

review: ## What `/review` runs first — the mechanical half of a code review
	@$(MAKE) --no-print-directory lint
	@echo "\nMechanical checks pass. For the judgement half — layering, N+1,"
	@echo "the Query/Zustand split, test placement — run /review in Claude Code."

format: ## Auto-fix what can be auto-fixed
	$(BACKEND) uv run ruff check --fix src tests
	$(BACKEND) uv run ruff format src tests

clean: ## Remove build artefacts, caches and volumes
	$(COMPOSE_DEV) down -v
	rm -rf frontend/dist frontend/node_modules backend/.venv backend/.pytest_cache
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
