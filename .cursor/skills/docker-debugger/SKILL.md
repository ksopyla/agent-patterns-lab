---
name: docker-debugger
description: >-
  Builds, runs, and debugs Docker Compose setups for examples. Use when Docker
  builds fail, containers won't start, inter-container networking breaks, or
  when debugging multi-service agent deployments.
---

# Docker Debugger

## When to Use

Trigger this skill when:
- `docker compose up --build` fails or a container exits unexpectedly
- An agent service can't reach another service (network/DNS issues)
- Debugging multi-container setups in Patterns 05+
- Investigating image build failures with the base Dockerfile

## Available MCP Tools

Use the Docker MCP (`project-0-agent-patterns-lab-docker`) for inspection:

| Tool | Purpose |
|------|---------|
| `list_containers` | See running/stopped containers and their status |
| `fetch_container_logs` | Read stdout/stderr from a specific container |
| `list_images` | Check built images and tags |
| `list_networks` | Inspect Docker networks for multi-service setups |
| `list_volumes` | Check persistent volumes (PostgreSQL, etc.) |
| `start_container` / `stop_container` | Control individual containers |
| `recreate_container` | Rebuild and restart a single container |

## Diagnostic Workflow

1. **Check container status**
   - Call `list_containers` to see which containers are running, exited, or restarting
   - Note exit codes: `0` = clean stop, `1` = app error, `137` = OOM killed

2. **Read logs for the failing container**
   - Call `fetch_container_logs` with the container name
   - Look for: import errors, missing env vars, port conflicts, connection refused

3. **Verify network connectivity** (multi-service)
   - Call `list_networks` to confirm all services share a network
   - Service DNS names match the `services:` keys in `docker-compose.yml`
   - Common fix: services on different networks can't reach each other

4. **Check image build**
   - Call `list_images` to verify the image was built
   - If missing, the build stage likely failed -- re-read build logs

5. **Fix and rebuild**
   - Fix the issue in code or config
   - Run `docker compose up --build` to rebuild

## Project-Specific Build Context

All examples use the base Dockerfile at `infra/docker/base/Dockerfile.agent`:
- Build context is always the repo root (`../..` from the example)
- `EXAMPLE_DIR` build arg points to the specific example folder
- Multi-stage build: `builder` installs deps, `runtime` copies artifacts
- `.env` file is passed via `env_file` in docker-compose

## Common Failures

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `ModuleNotFoundError` | Dependency missing in `pyproject.toml` | `uv add <package>` in the example, rebuild |
| `Connection refused` on port 8000 | App not binding to `0.0.0.0` | Set `--host 0.0.0.0` in uvicorn command |
| Container restarts in loop | Crash on startup (missing env var) | Check `.env` file, compare with `.env.example` |
| `network X not found` | Compose network not created | Run `docker compose down` then `up` again |
| Build fails at `uv sync` | Lock file out of sync | Run `uv lock` locally first, then rebuild |

## Shell Commands (PowerShell)

```powershell
# Build and run from example directory
docker compose up --build

# Rebuild single service
docker compose up --build agent

# View logs for a service
docker compose logs -f agent

# Full reset (remove containers, networks, volumes)
docker compose down -v
```
