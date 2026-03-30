# AGENTS.md

Automatically maintained by continual learning. Do not edit manually.

## Learned User Preferences

- Use PowerShell syntax for all terminal commands (Windows 11 environment)
- Use `uv` for all Python package and environment management, never pip or pyenv
- Use conventional commit format: `type(scope): description` — see `git-workflow` skill
- Use `gh` CLI for GitHub operations (PRs, issues, actions); GitHub MCP as alternative
- Write multi-line strings to temp files in PowerShell (no heredoc support)
- Prefer async-first Python with type hints on all functions
- Run tests with `uv run python scripts/testing/run_test_suite.py` or `uv run pytest`
- Run type checks with `uv run python scripts/linting/run_mypy.py`, never raw `mypy` across examples

## Learned Workspace Facts

- Base Docker image: `infra/docker/base/Dockerfile.agent` (multi-stage build)
- Each example is a uv workspace member with its own `pyproject.toml`
- Shared library: `libs/common/` imported as `agent_common`
- Environment variables loaded from `.env` (copy `.env.example`)
- Python version pinned to 3.14 via `.python-version`
- Project repo: `git@github.com:ksopyla/agent-patterns-lab.git`
- Branches: `dev` (working), `main` (stable)
- Monorepo: multiple `src/` packages exist across examples -- tools like mypy must run per-directory to avoid duplicate module conflicts
- CI commands in `.github/workflows/ci.yml` must use the same wrapper scripts as local dev (single source of truth)

## Pattern 02 Architecture Decisions

- Graph uses parallel fan-out / fan-in: `research_planner → [news_scanner | project_profiler | community_analyst] → intelligence_compiler`
- `research_planner` is the orchestrator: extracts `project_name` and `coin_ticker` into state so downstream nodes never receive raw user input for external API calls
- Data source ownership: `project_profiler` owns ALL CoinGecko data (market stats, price, developer_data); `news_scanner` owns news web search; `community_analyst` owns social sentiment web search (site: restrictions)
- `community_analyst` does NOT call CoinGecko -- eliminated prior duplication with `project_profiler`
- External API calls (CoinGecko) use retry with exponential backoff (3 attempts)
- Search nodes fire multiple targeted queries and deduplicate results by URL before passing to LLM
- No `_normalize_query` regex -- LLM extraction in research_planner replaced brittle regex parsing

## Rules vs Skills Architecture

Rules (always-applied, minimal context):
- `local-environment` — OS, shell, uv, gh, repo basics
- `project-vision` — one-liner + pointers to `docs/curriculum.md` and `docs/vision.md`
- `tech-stack` — Python/ruff/linting commands, Docker base image, project structure
- `testing-gate` — test requirements + pointer to `tester` skill
- `code-quality-gate` (glob-scoped) — quick checklist for `examples/*/src/**/*.py`

Skills (loaded on demand):
- `git-workflow` — branching, commits, PRs (was a rule, moved to skill)
- `langgraph-example-implementation` — LangGraph, FastAPI, LangSmith, verbose mode conventions and templates
- `example-scaffolder` — folder structure, Docker compose, pyproject templates
- `docker-debugger` — Docker troubleshooting and MCP tools
- `tester` — test strategy, pytest patterns, CI commands
- `runtime-verifier` — live Docker verification and smoke tests
- `example-readme-writer` — README structure and Mermaid diagrams
- `engineering-tracker` — CHANGELOG maintenance
- `agent-patterns-advisor` — architecture and pattern selection
- `agent-tools-and-platforms` — framework/library comparison and references
