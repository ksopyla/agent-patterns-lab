## Description

<!-- What does this PR do? Which lesson/example does it affect? -->

## Type of Change

- [ ] New lesson/example
- [ ] Enhancement to existing lesson
- [ ] Bug fix
- [ ] Infrastructure/CI change
- [ ] Documentation update

## Checklist

### Code
- [ ] Code follows the project's tech stack conventions (see `.cursor/rules/tech-stack.mdc`)
- [ ] Type hints added for all functions
- [ ] `VERBOSE=true` logging added for new agent nodes
- [ ] LangSmith tracing wired up via `setup_tracing()`

### Docker
- [ ] `docker-compose.yml` updated/created
- [ ] Tested locally with `docker compose up --build`
- [ ] Health endpoint returns `{"status": "ok"}`

### Documentation
- [ ] `README.md` follows the documentation template
- [ ] Architecture diagram (Mermaid) included
- [ ] "Running the Example" section with exact commands
- [ ] `docs/CHANGELOG.md` updated

### Testing
- [ ] Tests added/updated in `tests/`
- [ ] All tests pass (`make test`)
- [ ] Linting passes (`make lint`)
