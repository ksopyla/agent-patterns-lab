# AGENTS.md

## Cursor Cloud specific instructions

### Overview

Agent Patterns Lab is an educational monorepo teaching AI agent design patterns. Only **Lesson 1** (`examples/01-multi-agent-single-system/`) is currently implemented — a FastAPI app with a LangGraph multi-agent pipeline (planner → researcher → writer).

### Key commands

Standard dev commands are in the root `Makefile`:

- `make setup` — install all workspace dependencies (`uv sync --all-packages`)
- `make lint` — ruff check + ruff format check + mypy
- `make test` — run pytest
- `make fmt` — auto-format with ruff

### Running the Lesson 1 FastAPI app (non-Docker)

```bash
cd examples/01-multi-agent-single-system
uv run uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
```

The `/health` endpoint works without API keys. The `/run` endpoint requires a configured LLM provider (Azure OpenAI or Anthropic) — set keys in the root `.env` file (copy from `.env.example`).

### Known issues

- **Docker build**: The `infra/docker/base/Dockerfile.agent` uses `$(basename ${EXAMPLE_DIR})` to derive the package name, which produces `01-multi-agent-single-system` instead of the correct `example-01-multi-agent-single-system`. Docker Compose builds will fail until this is fixed. Use the direct uvicorn approach above instead.
- **mypy duplicate module**: Running `make lint` produces a mypy error about duplicate `tests` module names across workspace members. This is a pre-existing issue in the repo's mypy configuration.
- **ruff format**: Two files (`researcher.py`, `writer.py`) have minor formatting discrepancies that cause `ruff format --check` to fail. Run `make fmt` to fix.
- **Pydantic V1 warning**: On Python 3.14, `langchain_core` emits a `UserWarning` about Pydantic V1 compatibility. This is harmless and comes from upstream.

### LLM API keys

The agent pipeline requires at least one LLM provider configured in `.env`:

- **Azure OpenAI**: Set `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT`
- **Anthropic**: Set `ANTHROPIC_API_KEY` and `LLM_PROVIDER=anthropic`

Without these, the `/run` endpoint will return a 500 error. The `/health` endpoint always works.
