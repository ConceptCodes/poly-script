# Poly-Script Monorepo Task Runner
# Usage: just <recipe>

set dotenv-load := true

# Default recipe - show available commands
default:
    @just --list

# ──────────────────────────────────────────────────────────────────────────────
# DEVELOPMENT SERVERS
# ──────────────────────────────────────────────────────────────────────────────

# Start web app dev server
web:
    cd apps/web && bun run dev

# Start admin app dev server
admin:
    cd apps/admin && bun run dev

# Start marketing site dev server
marketing:
    cd apps/marketing && bun run dev

# Start API server
api:
    cd apps/api && uv run uvicorn main:app --reload

# Start all frontend apps (parallel)
frontend:
    just web & just admin & just marketing

# ──────────────────────────────────────────────────────────────────────────────
# BUILD
# ──────────────────────────────────────────────────────────────────────────────

# Build web app
build-web:
    cd apps/web && bun run build

# Build admin app
build-admin:
    cd apps/admin && bun run build

# Build marketing site
build-marketing:
    cd apps/marketing && bun run build

# Build all TypeScript apps
build-ts: build-web build-admin build-marketing

# ──────────────────────────────────────────────────────────────────────────────
# TESTING
# ──────────────────────────────────────────────────────────────────────────────

# Run all tests
test: test-ts test-py

# Run TypeScript tests
test-ts:
    cd apps/web && bun run test

# Run all Python tests
test-py:
    uv run pytest

# Run Python tests for a specific package
test-pkg pkg:
    uv run pytest {{ pkg }}/tests

# Run e2e tests
test-e2e:
    cd apps/web && bun run test:e2e

# ──────────────────────────────────────────────────────────────────────────────
# LINTING & FORMATTING
# ──────────────────────────────────────────────────────────────────────────────

# Lint all code
lint: lint-ts lint-py theme-guard

# Lint TypeScript code
lint-ts:
    cd apps/web && bun run lint
    cd apps/admin && bun run lint

# Lint Python code
lint-py:
    uv run ruff check .

# Guardrail: no app-level CSS variable definitions
theme-guard:
    ! rg --multiline --glob 'apps/**/src/**/*.css' --glob 'apps/**/src/**/*.scss' --glob 'apps/**/src/**/*.astro' ':root\s*\{[\s\S]*?--' apps

# Fix all lint issues
lint-fix: lint-fix-ts lint-fix-py

# Fix TypeScript lint issues
lint-fix-ts:
    cd apps/web && bun run lint:fix
    cd apps/admin && bun run lint:fix

# Fix Python lint issues
lint-fix-py:
    uv run ruff check --fix .

# Format all code
format: format-ts format-py

# Format TypeScript code
format-ts:
    cd apps/web && bun run format
    cd apps/admin && bun run format

# Format Python code
format-py:
    uv run ruff format .

# Check formatting without changes
format-check: format-check-ts format-check-py

# Check TypeScript formatting
format-check-ts:
    cd apps/web && bun run format:check
    cd apps/admin && bun run format:check

# Check Python formatting
format-check-py:
    uv run ruff format --check .

# ──────────────────────────────────────────────────────────────────────────────
# DEPENDENCIES
# ──────────────────────────────────────────────────────────────────────────────

# Install all dependencies
install: install-ts install-py

# Install TypeScript dependencies
install-ts:
    bun install

# Install Python dependencies (via uv workspace)
install-py:
    uv sync

# Update all dependencies
update: update-ts update-py

# Update TypeScript dependencies
update-ts:
    bun update

# Update Python dependencies
update-py:
    uv lock --upgrade

# ──────────────────────────────────────────────────────────────────────────────
# UTILITIES
# ──────────────────────────────────────────────────────────────────────────────

# Clean all build artifacts and caches
clean:
    rm -rf apps/web/dist apps/admin/dist apps/marketing/dist
    rm -rf **/__pycache__ **/.pytest_cache **/.ruff_cache
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# Type check TypeScript
typecheck:
    cd apps/web && bun run tsc --noEmit
    cd apps/admin && bun run tsc --noEmit

# Preview production build of web app
preview-web:
    cd apps/web && bun run preview

# Database migrations (via db)
db-migrate:
    cd packages/storage/db && uv run alembic upgrade head

# Generate new migration
db-migration name:
    cd packages/storage/db && uv run alembic revision --autogenerate -m "{{ name }}"

# ──────────────────────────────────────────────────────────────────────────────
# CI/CD
# ──────────────────────────────────────────────────────────────────────────────

# Run full CI checks
ci: install lint format-check typecheck test

# Pre-commit hook
pre-commit: lint-fix format typecheck test
