"""Typed state shared across all agent nodes in the full intelligence pipeline."""

from __future__ import annotations

from typing import Required, TypedDict


class AgentState(TypedDict, total=False):
    input: Required[str]
    plan: str
    news: str
    profile: str
    community: str
    report: str
