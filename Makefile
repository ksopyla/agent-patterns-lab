.PHONY: setup lint test fmt example clean

setup:
	uv sync --all-packages
	uv run pre-commit install --install-hooks --hook-type pre-commit --hook-type commit-msg

lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy libs/ examples/ --ignore-missing-imports --exclude "(^|/)tests/" --disable-error-code=misc --disable-error-code=unused-ignore

test:
	uv run pytest

fmt:
	uv run ruff format .
	uv run ruff check --fix .

# Preferred flow: cd examples/01-orchestrator-pipeline && docker compose up --build
# Shortcut usage: make example EX=01-orchestrator-pipeline
example:
	docker compose -f examples/$(EX)/docker-compose.yml up --build

example-down:
	docker compose -f examples/$(EX)/docker-compose.yml down -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
