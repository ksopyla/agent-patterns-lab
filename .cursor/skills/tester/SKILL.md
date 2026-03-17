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
   - `python scripts/testing/run_test_suite.py`
4. **Fix failures and re-run**
   - Repeat until green.

## Commands

- Full test suite with coverage:
  - `python scripts/testing/run_test_suite.py`
- Faster local run without coverage:
  - `python scripts/testing/run_test_suite.py --no-coverage`
- Direct pytest fallback:
  - `uv run pytest`

## CI and Commit Gate

- Local commit gate is enforced via `.pre-commit-config.yaml`:
  - hook id: `run-full-test-suite`
- Remote gate is enforced via `.github/workflows/ci.yml`:
  - runs on push to `main` and pull requests targeting `main`
  - executes unit + api + e2e tests with coverage

## Quality Checklist

Before marking testing work complete:
- [ ] Each changed example has `unit`, `api`, and `e2e` tests when applicable
- [ ] No test performs real LLM API calls (use mocks/stubs)
- [ ] API tests validate both success and failure paths
- [ ] E2E tests verify orchestration order and state handoff
- [ ] `python scripts/testing/run_test_suite.py` passes locally
