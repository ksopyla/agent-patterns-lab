FROM python:3.14-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY libs/ libs/
COPY examples/01-orchestrator-pipeline/pyproject.toml examples/01-orchestrator-pipeline/pyproject.toml

RUN uv sync --frozen --package "example-01-orchestrator-pipeline" --no-dev

FROM python:3.14-slim AS runtime

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY libs/common/src/agent_common/ /app/agent_common/
COPY examples/01-orchestrator-pipeline/src/ /app/src/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
