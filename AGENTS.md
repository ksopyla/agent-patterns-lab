# AGENTS.md

Automatically maintained by continual learning. Do not edit manually.

## Learned User Preferences

- Use PowerShell syntax for all terminal commands (Windows 11 environment)
- Use `uv` for all Python package and environment management, never pip or pyenv
- Use conventional commit format: `type(scope): description`
- Use GitHub MCP tools for PR/issue operations (`gh` CLI is installed as alternative tool)
- Write multi-line strings to temp files in PowerShell (no heredoc support)
- Prefer async-first Python with type hints on all functions
- Run tests with `python scripts/testing/run_test_suite.py` or `uv run pytest`

## Learned Workspace Facts

- Base Docker image: `infra/docker/base/Dockerfile.agent` (multi-stage build)
- Each example is a uv workspace member with its own `pyproject.toml`
- Shared library: `libs/common/` imported as `agent_common`
- Environment variables loaded from `.env` (copy `.env.example`)
- Python version pinned to 3.14 via `.python-version`
- Project repo: `git@github.com:ksopyla/agent-patterns-lab.git`
- Branches: `dev` (working), `main` (stable)
