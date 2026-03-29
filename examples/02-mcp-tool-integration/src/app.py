"""FastAPI application exposing the full Team 1 intelligence pipeline with MCP tools."""

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
from src.mcp_setup import close_mcp, init_mcp


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AsyncIterator[None]:
    setup_tracing()
    await init_mcp()
    fastapi_app.state.graph = build_graph()
    verbose_log("System", "FastAPI application started with MCP connections")
    yield
    await close_mcp()
    verbose_log("System", "FastAPI application shutting down")


app = FastAPI(
    title="Pattern 02: MCP Tool Integration",
    description=(
        "Full Team 1 intelligence pipeline (5 agents) with MCP-based tool access: "
        "crypto-intelligence MCP (CoinGecko) and Brave Search MCP (web search)."
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
