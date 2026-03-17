"""FastAPI application exposing the full Team 1 intelligence pipeline with MCP tools."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from agent_common.tracing import setup_tracing, verbose_log
from fastapi import FastAPI
from pydantic import BaseModel

from src.agents.graph import build_graph
from src.mcp_setup import close_mcp, init_mcp


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    setup_tracing()
    await init_mcp()
    verbose_log("System", "FastAPI application started with MCP connections")
    yield
    await close_mcp()
    verbose_log("System", "FastAPI application shutting down")


app = FastAPI(
    title="Pattern 02: MCP Tool Integration",
    description="Full Team 1 intelligence pipeline (5 agents) with MCP-based tool access to CoinGecko data.",
    version="0.1.0",
    lifespan=lifespan,
)


class RunRequest(BaseModel):
    input: str


class RunResponse(BaseModel):
    report: str
    plan: str
    news: str
    profile: str
    community: str


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/run", response_model=RunResponse)
async def run(request: RunRequest) -> RunResponse:
    verbose_log("System", f"Received request: {request.input[:100]}")

    graph = build_graph()
    result = await graph.ainvoke({"input": request.input})

    verbose_log("System", "Pipeline complete, returning response")

    return RunResponse(
        report=result.get("report", ""),
        plan=result.get("plan", ""),
        news=result.get("news", ""),
        profile=result.get("profile", ""),
        community=result.get("community", ""),
    )
