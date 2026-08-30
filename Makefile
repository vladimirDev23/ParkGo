.PHONY: up down logs backend-install backend-run backend-test ios-check lint typecheck test verify

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f backend

backend-install:
	cd backend && uv sync --locked --extra dev

backend-run:
	cd backend && uv run uvicorn app.main:app --reload

backend-test:
	cd backend && uv run pytest

lint:
	cd backend && uv run ruff check .
	cd backend && uv run ruff format --check .

typecheck:
	cd backend && uv run mypy app

test: backend-test

ios-check:
	swift run --package-path ios ParkGoCoreChecks

verify: lint typecheck test ios-check
