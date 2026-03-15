"""Typed state shared across all agent nodes."""

from __future__ import annotations

from typing import TypedDict


class AgentState(TypedDict, total=False):
    input: str
    plan: str
    research: str
    output: str
