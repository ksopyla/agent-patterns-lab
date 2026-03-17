"""Typed state shared across all agent nodes in the intelligence pipeline."""

from __future__ import annotations

from typing import Required, TypedDict


class AgentState(TypedDict, total=False):
    input: Required[str]
    plan: str
    news: str
    report: str
