---
name: runtime-verifier
description: Verifies running examples and services through Docker, health checks, manual requests, container logs, and MCP-backed observability tools such as LangSmith or Auth0. Use after implementation when you need smoke tests, runtime debugging, manual QA, trace inspection, or external-service verification.
---

# Runtime Verifier

## Responsibility

This skill owns live runtime verification after code exists.

Use it to:
- start or inspect Docker Compose services
- run health checks and representative requests
- inspect container logs and runtime warnings
- verify Hosted LangSmith traces and tags through MCP or direct API tools
- verify external service behavior such as Auth0 when the relevant MCP server exists
- summarize findings, residual risks, and confidence gaps

Do not use it to:
- author or restructure pytest suites; use [`../tester/SKILL.md`](../tester/SKILL.md)
- choose architecture or service boundaries; use [`../agent-patterns-advisor/SKILL.md`](../agent-patterns-advisor/SKILL.md)
- make large implementation changes unless the user explicitly asks for them

## When To Use

Trigger this skill when:
- the user asks to "test it", "verify it", "run it", or "smoke test it"
- Docker containers, startup logs, or runtime behavior must be checked
- LangSmith traces, runs, tags, or metadata must be inspected
- external integrations such as Auth0 need manual verification
- automated tests pass but you still need runtime confidence

## Core Principles

- Prefer real but minimal verification: one healthy startup and one representative request beat broad ad hoc clicking.
- Check existing running terminals and containers before starting new long-running processes.
- Keep verification secrets out of committed files. For committed MCP configs, load credentials from `.env` or local environment, never inline keys.
- Treat runtime verification as read-mostly. Do not mutate production-like services unless the task requires it.
- Report findings first when something is wrong. If no issues are found, say that explicitly and list what was actually verified.

## MCP Guidance

- Prefer repo-configured MCP servers when they fit the task:
  - `langsmith` for runs, traces, prompts, datasets, and projects
  - `auth0` for Auth0 tenant inspection and auth-related checks
  - `docker` for container-aware workflows when it is more effective than shell commands
- For committed `.cursor/mcp.json` entries, use wrappers such as `scripts/mcp-env.mjs` so API keys come from `.env` rather than the repository file.
- If LangSmith uses a regional endpoint, make sure `LANGSMITH_ENDPOINT` is present in `.env` so the MCP server and app use the same region.

## Verification Workflow

1. Confirm the target surface.
   - Example: `examples/01-orchestrator-pipeline`
   - Endpoints, expected behavior, and what counts as success

2. Inspect runtime state before starting anything.
   - Check existing terminals or containers
   - Avoid duplicate dev servers or duplicate Compose stacks

3. Start the service with the normal project workflow.
   - Prefer the example-local `docker compose up --build`
   - Wait for a healthy container or successful startup log

4. Exercise the service.
   - Hit `/health`
   - Send one or two representative requests
   - Prefer `endpoints.http` examples or stable payloads from the README

5. Inspect runtime evidence.
   - Container logs for warnings, stack traces, retries, auth failures, or tool errors
   - LangSmith traces for root runs, node ordering, tags, metadata, and child tool calls
   - External service logs or responses when relevant

6. Summarize confidence.
   - What was verified
   - What failed or looked suspicious
   - What was not checked

## LangSmith Checklist

When LangSmith tracing is expected:
- Confirm startup logs show tracing enabled without auth or ingest errors
- Trigger at least one real request so a trace is created
- Inspect recent runs and verify:
  - the expected project is used
  - root and child runs appear
  - expected tags are present, such as `example:...`, `pattern:...`, `env:...`, `runtime:...`, `provider:...`
  - metadata looks sane for the example and environment
- If traces are missing, check:
  - `LANGSMITH_TRACING`
  - `LANGSMITH_API_KEY`
  - `LANGSMITH_ENDPOINT`
  - whether the request actually reached the traced code path

## Docker And Log Checklist

- Container reaches `healthy` when a health check exists
- Startup logs do not contain auth failures, unhandled exceptions, or repeated retries
- Request logs show expected status codes and timing
- Warnings that do not block success are still reported if they may matter later

## Reporting Format

Use this order:
1. Runtime status
2. Findings
3. Verified evidence
4. Residual risks or gaps

If there are no findings, say:
- no runtime issues found in the checks performed

Then list the exact checks completed.

## Boundaries

- Do not convert manual verification into brittle automated tests unless the user asks.
- Do not silently change `.env` secrets or committed MCP config values to real tokens.
- Do not keep extra containers running unless the user wants them left up.
