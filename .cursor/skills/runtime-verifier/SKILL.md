---
name: runtime-verifier
description: >-
  Live runtime verification for examples and Docker Compose services: health checks,
  representative HTTP requests (e.g. POST /run), container logs, LangSmith traces via MCP,
  smoke tests, manual QA, "verify it works", "is it running", "check the stack",
  "runtime check", "smoke test", "test in Docker". Use this skill whenever verification
  involves a running container or real request path—not pytest alone. Complements
  ../tester/SKILL.md (automated tests). After implementation or when debugging startup.
---

# Runtime Verifier

## Agent activation (read this first)

**When this skill applies:** the user asks to verify, smoke-test, run, or confirm that an **example or service works in Docker** (or similar: "working properly", "runtime check", "does it run", "check logs", "see traces").

**Required behavior for the agent:**

1. **Do not treat `pytest` (or unit/API tests alone) as sufficient** for "verify it works" when the user expects a **live** stack—tests are owned by [`../tester/SKILL.md`](../tester/SKILL.md). You may run pytest *in addition* after runtime checks, unless the user explicitly asks for tests only.
2. Execute **all steps in [Mandatory verification steps](#mandatory-verification-steps)** below unless the user **narrows scope** (e.g. "only health check" or "logs only"). If you skip a mandatory step, **say which step and why** in the report.
4. End with the **[Reporting Format](#reporting-format)** section, including **what was not checked**.

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
- the user asks to "test it", "verify it", "run it", or "smoke test it" **in a Docker / example context**
- Docker containers, startup logs, or runtime behavior must be checked
- LangSmith traces, runs, tags, or metadata must be inspected
- external integrations such as Auth0 need manual verification
- automated tests pass but you still need runtime confidence

## Mandatory verification steps

Complete these in order for a **full** verification of an example under `examples/`:

1. **Confirm target** — Which folder, which endpoints, what "success" means (see `endpoints.http` and README).
2. **Pre-flight** — Check for existing containers (`docker ps`) or compose stacks that would conflict; avoid duplicate servers on the same ports.
3. **Start stack** — From the example folder: `docker compose up --build` (detached `-d` is fine). Wait until the service is **healthy** if a healthcheck exists, or until startup logs show the app listening.
4. **Exercise HTTP** — `GET` `/health` (or documented health URL). Then at least **one representative request** that hits the main code path (e.g. `POST /run` using a body from `endpoints.http`). Confirm the response shape or status matches expectations.
5. **Logs** — `docker compose logs` (or `logs <service>`) and scan for errors, trace/auth failures, repeated retries. Note **warnings** that may matter (e.g. deprecation noise).
6. **LangSmith (if tracing is on)** — After a real request, verify traces (see [LangSmith Checklist](#langsmith-checklist)). Use MCP tools when available.
7. **Teardown** — `docker compose down` unless the user asked to leave containers running.
8. **Report** — Use [Reporting Format](#reporting-format).

## Core Principles

- Prefer real but minimal verification: one healthy startup and one representative request beat broad ad hoc clicking.
- Check existing running terminals and containers before starting new long-running processes.
- Keep verification secrets out of committed files. For committed MCP configs, load credentials from `.env` or local environment, never inline keys.
- Treat runtime verification as read-mostly. Do not mutate production-like services unless the task requires it.
- Report findings first when something is wrong. If no issues are found, say that explicitly and list what was actually verified.

## MCP Guidance

- Prefer repo-configured MCP servers when they fit the task. **Server names in Cursor are often prefixed** (e.g. `project-0-agent-patterns-lab-langsmith`), not the short key from `.cursor/mcp.json`. **Before calling a tool:** read the tool schema from the project `mcps/<server>/tools/` descriptors (or the system "Available MCP servers" list) and use the **actual server identifier** shown there.
- Logical roles:
  - LangSmith-style server: runs, traces, prompts, datasets, projects
  - Auth0: tenant inspection when present
  - Docker: container-aware workflows when more effective than shell
- For committed `.cursor/mcp.json` entries, use wrappers such as `scripts/mcp-env.mjs` so API keys come from `.env` rather than the repository file.
- If LangSmith uses a regional endpoint, make sure `LANGSMITH_ENDPOINT` is present in `.env` so the MCP server and app use the same region.

## Verification Workflow

1. Confirm the target surface.
   - Example: `examples/01-orchestrator-pipeline`
   - Endpoints, expected behavior, and what counts as success

2. Inspect runtime state before starting anything.
   - Check existing terminals or containers
   - Avoid duplicate dev servers or duplicate Compose stacks

3. Start the docker compose stack.
   - Prefer the example-local `docker compose up --build`
   - Wait for a healthy container or successful startup log

4. Exercise the service.
   - Hit `/health` (or the documented health endpoint)
   - Send one or two **representative** requests so the main service flow runs (agents collaborate as designed). Use `endpoints.http` or stable payloads from the README. **Check the response body or status.**

5. Inspect runtime evidence.
   - Container logs for warnings, stack traces, retries, auth failures, or tool errors
   - LangSmith traces for root runs, node ordering, tags, metadata, and child tool calls (when applicable)
   - External service logs or responses when relevant: postgres, redis, auth0, etc.

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
  - root run exists; expand or fetch child runs when verifying node ordering matters
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

Then list the **exact checks completed** (health, which POST/GET, logs reviewed, LangSmith MCP or UI, teardown).

## Boundaries

- Do not convert manual verification into brittle automated tests unless the user asks.
- Do not silently change `.env` secrets or committed MCP config values to real tokens.
- Do not keep extra containers running unless the user wants them left up.
