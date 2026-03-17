"""FastAPI application exposing the crypto intelligence pipeline."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from agent_common.tracing import setup_tracing, verbose_log
from fastapi import FastAPI
from pydantic import BaseModel

from src.agents.graph import build_graph


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    setup_tracing()
    verbose_log("System", "FastAPI application started")
    yield
    verbose_log("System", "FastAPI application shutting down")


app = FastAPI(
    title="Pattern 01: Orchestrator Pipeline",
    description="Three-agent crypto intelligence pipeline (Research Planner, News Scanner, Intelligence Compiler).",
    version="0.1.0",
    lifespan=lifespan,
)


class RunRequest(BaseModel):
    input: str


class RunResponse(BaseModel):
    report: str
    plan: str
    news: str


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
    )
