---
name: git-workflow
description: >-
  Git branching, conventional commits, and PR workflow. Use when committing
  code, creating branches, opening pull requests, or any git operation
  that needs project conventions.
---

# Git Workflow

## Branching
- `main` -- stable, release-ready code
- `dev` -- integration branch for in-progress work
- Feature branches off `dev` when needed: `feat/NN-short-name`

## Commit Messages

Use conventional commits with optional scope:

```
type(scope): short description

Optional body explaining motivation.
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`
Scopes: pattern number or area, e.g. `01`, `common`, `infra`, `ci`

Examples:
- `feat(02): add community analyst agent with MCP tool calls`
- `test(01): add e2e tests for orchestrator pipeline graph`
- `docs: expand README with pattern progression overview`

## Pull Requests
- PRs merge `dev` → `main` after a set of related changes
- Use `gh` CLI (preferred) or GitHub MCP for PR creation
- Write PR body to a temp file and use `--body-file` (PowerShell has no heredocs)
- Use `@" ... "@` here-strings only for simple cases (no special chars)
