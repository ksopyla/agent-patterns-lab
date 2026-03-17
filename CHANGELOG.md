# Changelog

All notable changes to this project are documented here.

## [2026-03-15] Initial Repository Setup

### Added
- Root project configuration with uv workspace (`pyproject.toml`)
- Shared library `libs/common/` with LLM config, LangSmith tracing, and verbose logging utilities
- Cursor rule `tech-stack.mdc` for Python, uv, Docker, LangGraph, FastAPI conventions
- Cursor skills: agent-patterns-advisor, documentation-writer, example-scaffolder, engineering-tracker
- GitHub Actions workflows: CI (lint, type-check, test), security (audit, scanning), deploy (Azure)
- PR template and CODEOWNERS
- Pre-commit hooks: ruff, mypy, detect-secrets, conventional commits
- Base Docker image for agent services (`infra/docker/base/Dockerfile.agent`)
- Curriculum document with 8-lesson Phase 1 plan
- Phase 2 planning document (conversational tutoring system)
- Example 01: Multi-Agent Single System (LangGraph + FastAPI + Docker)

### Architecture Decisions
- **uv over Poetry**: 10-100x faster, PEP 621 native, bundles Python version management
- **Auth0 over Keycloak**: Enterprise standard, free tier sufficient, purpose-built AI agent features
- **LangSmith from day one**: Tracing integrated in shared lib, every agent traced by default
- **A2A + MCP complementary**: MCP for tool access, A2A for agent-to-agent communication
- **Azure Container Apps for deployment**: Stateful, event-driven, fits LangGraph's requirements
- **Verbose mode as cross-cutting concern**: Every agent logs reasoning to stdout when VERBOSE=true

### Dependencies
- langgraph >= 0.4 (agent orchestration)
- langchain-openai >= 0.3 (Azure OpenAI integration)
- langchain-anthropic >= 0.3 (Claude integration)
- langsmith >= 0.3 (tracing and observability)
- fastapi >= 0.115 (HTTP endpoints)
- pydantic >= 2.0 (data validation)
- pydantic-settings >= 2.0 (environment configuration)
