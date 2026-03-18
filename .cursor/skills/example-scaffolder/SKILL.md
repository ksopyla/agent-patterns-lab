---
name: example-scaffolder
description: >-
  Generates the folder structure, Docker files, compose files, and README
  scaffolding for new examples. Use when creating a new `examples/NN-name/`
  folder, starting a new pattern, or adding a new runnable service inside an
  example.
---

# Example Scaffolder

## When to Use

Trigger this skill when:
- Creating a new `examples/NN-name/` folder
- Starting work on a new pattern
- Adding a new runnable service to an existing example

This skill focuses on:
- example folder structure
- `Dockerfile` and `docker-compose.yml`
- `README.md` run instructions
- HTTP verification helpers such as `endpoints.http`

For LangChain/LangGraph application code, agent wiring, and test templates, use
the companion skill at [`../langgraph-example-implementation/SKILL.md`](../langgraph-example-implementation/SKILL.md).

## Folder Structure

Every example should start with this structure:

```text
examples/NN-name/
├── Dockerfile
├── pyproject.toml
├── README.md
├── docker-compose.yml
├── endpoints.http
├── src/
│   ├── __init__.py
│   ├── app.py
│   └── agents/
│       ├── __init__.py
│       └── [agent_name].py
└── tests/
    ├── conftest.py
    ├── unit/
    │   └── test_*.py
    ├── api/
    │   └── test_*.py
    └── e2e/
        └── test_*.py
```

Notes:
- Examples should be runnable from inside their own folder with `docker compose up --build`.
- Examples may still depend on the repo-root `.env`, workspace `uv.lock`, and `libs/common`.
- Do not create an example-local `config.py` for shared LLM settings. Use `agent_common.config`.

## `pyproject.toml` Template

```toml
[project]
name = "example-NN-name"
version = "0.1.0"
description = "Pattern NN: [Title]"
requires-python = ">=3.14"
dependencies = [
    "langgraph>=0.4",
    "langchain-core>=0.3",
    "langchain-community>=0.3",
    "langchain-openai>=0.3",
    "langchain-anthropic>=0.3",
    "langsmith>=0.3",
    "fastapi>=0.115",
    "uvicorn>=0.34",
    "pydantic>=2.0",
    "httpx>=0.28",
    "agent-common",
]

[tool.uv.sources]
agent-common = { workspace = true }
```

Add extra dependencies only when the example truly needs them, for example:
- `ddgs` if using `DuckDuckGoSearchResults`
- `langchain-mcp-adapters` and `mcp` for MCP examples
- `python-jose` for auth examples
- database drivers for persistence examples

## `Dockerfile` Template

Each example should have its own small, explicit `Dockerfile`. Avoid hidden
folder-name inference in Docker build args.

```dockerfile
FROM python:3.14-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY libs/ libs/
COPY examples/NN-name/pyproject.toml examples/NN-name/pyproject.toml

RUN uv sync --frozen --package "example-NN-name" --no-dev

FROM python:3.14-slim AS runtime

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY libs/common/src/agent_common/ /app/agent_common/
COPY examples/NN-name/src/ /app/src/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Rules:
- Keep the package name explicit in the Dockerfile.
- Keep the copied example path explicit in the Dockerfile.
- Default the command to `uvicorn src.app:app ...` unless the example is not HTTP-based.
- For extra services in the same example, prefer compose `command:` overrides over extra Dockerfiles unless runtime contents differ.

## `docker-compose.yml` Template

```yaml
services:
  agent:
    build:
      context: ../..
      dockerfile: examples/NN-name/Dockerfile
    ports:
      - "8000:8000"
    env_file:
      - ../../.env
    environment:
      - VERBOSE=${VERBOSE:-true}
    healthcheck:
      test: ["CMD", "python", "-c", "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"]
      interval: 10s
      timeout: 5s
      retries: 3
```

Rules:
- The primary UX must be `cd examples/NN-name && docker compose up --build`.
- Keep `context: ../..` so examples can reuse the workspace lockfile and shared library.
- Make any root `.env` dependency explicit in the README.
- Add extra services only when the pattern truly needs them.

## `endpoints.http` Template

```http
### Health
GET http://localhost:8000/health

### Run pipeline
POST http://localhost:8000/run
Content-Type: application/json

{
    "input": "Research the Arbitrum crypto project"
}
```

## `README.md` Template

Use this outline in every new example README:

````markdown
# Pattern NN: [Title]

> One-sentence summary of the pattern.

## What You'll Learn

- Key concept 1
- Key concept 2

## The Problem

Explain what the previous pattern could not do and why this pattern exists.

## Architecture

Include a Mermaid diagram when the architecture is not obvious.

## Running the Example

```bash
# From the repository root
cp .env.example .env
# Fill in the required API keys

# Run from inside the example folder
cd examples/NN-name
docker compose up --build

# Verify it's healthy
curl http://localhost:8000/health
```

### Optional repo-root shortcut

```bash
make example EX=NN-name
```

## Verification

Show one concrete API request and expected response shape.

Mention `endpoints.http` if the example includes one.

## Exercises

1. Extension idea one
2. Extension idea two

## Trade-offs

| Advantage | Limitation |
|-----------|-----------|
| ... | ... |
````

README rules:
- The primary run path should always be the example-folder flow.
- Root-level shortcuts should be clearly marked as optional.
- If the example depends on the repo-root `.env`, say so directly.
- Keep the README self-sufficient: a developer should not need to inspect `infra/`.

## Scaffolding Workflow

1. Create the example folder structure and `pyproject.toml`.
2. Add an example-local `Dockerfile`.
3. Add an example-local `docker-compose.yml`.
4. Add `endpoints.http` for quick verification.
5. Draft the example README with example-folder-first run instructions.
6. Then switch to the LangGraph code skill for `src/` and `tests/`.

## Checklist

After scaffolding, verify:
- [ ] The example has its own `Dockerfile`
- [ ] `docker-compose.yml` works from inside the example folder
- [ ] The compose file points at `examples/NN-name/Dockerfile`
- [ ] The Dockerfile uses explicit package and source paths
- [ ] `README.md` documents the example-folder run flow first
- [ ] `README.md` explains the repo-root `.env` dependency if present
- [ ] `endpoints.http` exists for HTTP examples
- [ ] `pyproject.toml` lists `agent-common` as a workspace dependency
- [ ] `tests/unit`, `tests/api`, and `tests/e2e` all exist
