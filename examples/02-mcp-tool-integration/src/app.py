"""FastAPI application exposing the crypto intelligence pipeline via REST.

This is the Software 2.0 entry point (POST /run). The Software 3.0 entry point
is the MCP server in src/mcp_servers/crypto_intelligence.py, which exposes
the same pipeline as an MCP tool that any AI client can call.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import cast

from agent_common.tracing import build_langsmith_run_config, setup_tracing, verbose_log
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from src.agents.graph import build_graph


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AsyncIterator[None]:
    setup_tracing()
    fastapi_app.state.graph = build_graph()
    verbose_log("System", "FastAPI application started")
    yield
    verbose_log("System", "FastAPI application shutting down")


app = FastAPI(
    title="Pattern 02: MCP Tool Integration",
    description=(
        "Crypto intelligence pipeline (5 agents). REST entry point at POST /run. "
        "MCP entry point at the crypto-intelligence MCP server (:8001)."
    ),
    version="0.1.0",
    lifespan=lifespan,
)


class RunRequest(BaseModel):
    input: str = Field(min_length=3, max_length=500, description="Crypto project query to research")


class RunResponse(BaseModel):
    report: str
    plan: str
    news: str
    profile: str
    community: str


def _pipeline_run_config() -> RunnableConfig:
    """Build trace metadata for the public pipeline invocation."""
    return cast(
        RunnableConfig,
        build_langsmith_run_config(
            example_name="02-mcp-tool-integration",
            pattern_slug="mcp-tool-integration",
            run_name="pattern-02-mcp-tool-integration",
        ),
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/run", response_model=RunResponse)
async def run(request: RunRequest) -> RunResponse | JSONResponse:
    verbose_log("System", f"Received request: {request.input[:100]}")

    try:
        result = await app.state.graph.ainvoke(
            {"input": request.input},
            config=_pipeline_run_config(),
        )
    except Exception as exc:
        verbose_log("System", f"Pipeline failed: {exc}")
        return JSONResponse(
            status_code=502,
            content={"error": "pipeline_failed", "detail": str(exc)},
        )

    verbose_log("System", "Pipeline complete, returning response")

    return RunResponse(
        report=result.get("report", ""),
        plan=result.get("plan", ""),
        news=result.get("news", ""),
        profile=result.get("profile", ""),
        community=result.get("community", ""),
    )
