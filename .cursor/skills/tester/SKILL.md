---
name: tester
description: >-
  Builds and maintains a complete test strategy for examples: unit, API, and
  end-to-end tests. Use when adding features, refactoring agents, creating new
  examples, reviewing test coverage, or preparing changes for commit/PR.
---

# Tester

## When to Use

Trigger this skill when:
- Adding or changing code in `examples/*/src/` or `libs/*/src/`
- Creating a new example folder
- Improving confidence before commit or pull request
- Investigating regressions in pipeline flow or API behavior

## Safety Rules
- Do not rely on live LLM providers in tests.
- Prefer deterministic tests with mocks/stubs.
- Keep API and e2e tests in CI-safe form (no external services required unless explicitly marked and isolated).
- When mocking LangChain/MCP tool objects, configure `.ainvoke` explicitly:
  `mock_tool.ainvoke = AsyncMock(return_value='...')`.
  Do NOT use `AsyncMock(return_value='...')` alone -- that configures the mock
  as a callable, but agent code calls `tool.ainvoke(...)`, which creates an
  unconfigured child mock returning a MagicMock instead of the expected value.

## Test Architecture Standard

For every example, keep tests in:

```text
examples/NN-name/tests/
├── unit/
│   └── test_*.py
├── api/
│   └── test_*.py
└── e2e/
    └── test_*.py
```

Coverage intent:
- **unit**: isolate pure logic and individual agent nodes with mocks/stubs
- **api**: validate FastAPI endpoints (`/health`, request validation, response model)
- **e2e**: validate graph orchestration and cross-node state flow

## Default Workflow

1. **Discover impacted examples**
   - Check changed files under `examples/` and `libs/`.
2. **Update tests by scope**
   - Behavior logic changed -> update `tests/unit/`
   - Endpoint schema/flow changed -> update `tests/api/`
   - Graph wiring/agent sequence changed -> update `tests/e2e/`
3. **Run complete suite**
   - `uv run python scripts/testing/run_test_suite.py`
4. **Fix failures and re-run**
   - Repeat until green.
5. **Run full CI checks locally**
   - After all tests pass, run the same checks that CI enforces.
     Most mypy and lint errors surface here, not during pytest.
   - `uv run ruff check .`
   - `uv run ruff format --check .`
   - `uv run python scripts/linting/run_mypy.py`
   - Fix every error before proceeding -- CI will reject the same issues.
6. **Agent Review -- inspect tests for common issues**
   - Re-read the new/changed test files and look for:
     - Missing or incorrect type annotations (mypy will flag these)
     - Imports of modules that don't exist or have moved
     - Mock objects with misconfigured `.ainvoke` (see Safety Rules)
     - Assertions that compare wrong types (e.g. `str` vs `dict`)
     - Leftover `# type: ignore` comments that hide real errors
     - Tests that accidentally depend on execution order or shared state
   - Fix every issue found, then re-run steps 3-5 until clean.

## Commands

- Full test suite with coverage:
  - `uv run python scripts/testing/run_test_suite.py`
- Faster local run without coverage:
  - `uv run python scripts/testing/run_test_suite.py --no-coverage`
- Direct pytest fallback:
  - `uv run pytest`
- Lint:
  - `uv run ruff check .`
- Format check:
  - `uv run ruff format --check .`
- Type check (per-directory, avoids duplicate module errors):
  - `uv run python scripts/linting/run_mypy.py`

## CI and Commit Gate

- Local commit gate is enforced via `.pre-commit-config.yaml`:
  - hook id: `run-full-test-suite`
- Remote gate is enforced via `.github/workflows/ci.yml`:
  - runs on push to `main` and pull requests targeting `main`
  - CI runs **all** of: ruff check, ruff format, mypy, pytest with coverage
  - **Every command in CI must pass locally before pushing.**

## Quality Checklist

Before marking testing work complete:
- [ ] Each changed example has `unit`, `api`, and `e2e` tests when applicable
- [ ] No test performs real LLM API calls (use mocks/stubs)
- [ ] API tests validate both success and failure paths
- [ ] E2E tests verify orchestration order and state handoff
- [ ] `uv run python scripts/testing/run_test_suite.py` passes locally
- [ ] `uv run ruff check .` reports no errors
- [ ] `uv run ruff format --check .` reports no reformatting needed
- [ ] `uv run python scripts/linting/run_mypy.py` passes with zero errors
- [ ] Agent Review step completed -- no type issues, mock misconfigurations, or stale imports remain
