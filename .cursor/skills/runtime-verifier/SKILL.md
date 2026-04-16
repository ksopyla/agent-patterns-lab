---
name: runtime-verifier
description: >-
  Live runtime verification and Docker troubleshooting for examples: health checks,
  representative HTTP requests, container logs, LangSmith traces, build failures,
  smoke tests. Use when the user says "verify it", "run it", "smoke test", "check logs",
  "Docker build fails", or "container won't start". Complements ../tester/SKILL.md
  (automated pytest).
---

# Runtime Verifier

## Responsibility

This skill owns live runtime verification and Docker troubleshooting.

Use it to:
- start, inspect, and debug Docker Compose services
- run health checks and representative requests
- diagnose build failures, container crashes, and networking issues
- inspect container logs and runtime warnings
- verify LangSmith traces and tags via MCP
- summarize findings, residual risks, and confidence gaps

Do not use it to:
- author or restructure pytest suites; use [`../tester/SKILL.md`](../tester/SKILL.md)
- choose architecture or service boundaries; use [`../agent-patterns-advisor/SKILL.md`](../agent-patterns-advisor/SKILL.md)

## Trigger Conditions

- "verify it", "run it", "smoke test", "check the stack", "is it running"
- Docker build fails or a container exits unexpectedly
- Container networking or inter-service connectivity issues
- LangSmith traces, runs, or metadata need inspection
- Automated tests pass but live runtime confidence is needed

## Mandatory Verification Steps

Complete in order for a full verification of an example under `examples/`:

1. **Confirm target** — folder, endpoints, success criteria (see `endpoints.http` and README).
2. **Pre-flight** — `docker ps` to check for existing containers; avoid port conflicts.
3. **Start stack** — `docker compose up --build` from the example folder. Wait for healthy status or startup logs.
4. **Exercise HTTP** — `GET /health`, then at least one representative request (e.g. `POST /run`). Check response shape.
5. **Logs** — `docker compose logs` — scan for errors, auth failures, retries. Note warnings.
6. **LangSmith** (if tracing is on) — verify traces exist with expected project, tags, and metadata. See [LangSmith Checklist](#langsmith-checklist).
7. **Teardown** — `docker compose down` unless user wants containers left running.
8. **Report** — use [Reporting Format](#reporting-format).

If the user narrows scope (e.g. "logs only"), skip other steps but say which were skipped.

## Docker Build Context

All examples use `infra/docker/base/Dockerfile.agent`:
- Build context is the repo root (`../..` from example folder)
- Compose sets `PACKAGE_NAME`, `EXAMPLE_PYPROJECT`, and `EXAMPLE_SRC`
- Multi-stage build: `builder` installs deps, `runtime` copies artifacts
- `.env` file passed via `env_file` in docker-compose

## Common Failures

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `ModuleNotFoundError` | Dependency missing in `pyproject.toml` | `uv add <package>`, rebuild |
| `Connection refused` on port 8000 | App not binding to `0.0.0.0` | Set `--host 0.0.0.0` in uvicorn |
| Container restarts in loop | Missing env var on startup | Check `.env` vs `.env.example` |
| `network X not found` | Compose network not created | `docker compose down` then `up` |
| Build fails at `uv sync` | Lock file out of sync | `uv lock` locally, then rebuild |

## Docker MCP Tools

Use the Docker MCP for inspection when shell commands are insufficient:

| Tool | Purpose |
|------|---------|
| `list_containers` | Running/stopped containers and status |
| `fetch_container_logs` | stdout/stderr from a container |
| `list_images` | Built images and tags |
| `list_networks` | Docker networks for multi-service setups |
| `list_volumes` | Persistent volumes (PostgreSQL, etc.) |

## LangSmith Checklist

When tracing is expected:
- Startup logs show tracing enabled without auth errors
- After a real request, verify: project name, root run, expected tags (`example:...`, `pattern:...`, `env:...`), sane metadata
- If traces are missing, check `LANGSMITH_TRACING`, `LANGSMITH_API_KEY`, `LANGSMITH_ENDPOINT`

## MCP Guidance

- Server names in Cursor are prefixed (e.g. `project-0-agent-patterns-lab-langsmith`). Read tool schemas before calling.
- For committed `.cursor/mcp.json` entries, use `scripts/mcp-env.mjs` so API keys come from `.env`.
- If LangSmith uses a regional endpoint, ensure `LANGSMITH_ENDPOINT` is in `.env`.

## Reporting Format

1. Runtime status
2. Findings
3. Verified evidence
4. Residual risks or gaps

If clean: "no runtime issues found" + list exact checks completed.

## Boundaries

- Do not convert manual verification into automated tests unless asked.
- Do not change `.env` secrets or MCP config values.
- Do not keep containers running unless asked.
