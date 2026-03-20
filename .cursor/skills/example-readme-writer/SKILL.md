---
name: example-readme-writer
description: >-
  Produces high-signal pattern READMEs, example landing pages, and professional
  documentation with Mermaid diagrams. Use when creating or refreshing example
  README files, pattern docs, blog posts, LinkedIn drafts, or any
  documentation that must be technically faithful and easy to scan on GitHub.
---

# Documentation Writer

## When to Use

Use this skill for:
- example or pattern `README.md` files
- README refreshes focused on conversion, clarity, or structure
- documentation that must work well on GitHub and in exported formats
- blog or LinkedIn drafts that will be derived from example docs

If the README came from `example-scaffolder`, treat that README as a shell only.
This skill owns the final structure, narrative, and polish.

## Before Writing

Do not write a finished README from assumptions. Read the real implementation first:
- app entrypoint and agent wiring
- tests that define the actual API and error behavior
- `Dockerfile`, `docker-compose.yml`, and `endpoints.http`
- `.env.example` and shared config if env vars or provider selection matter
- understand how example fits into the overall ../docs/curriculum.md and ../docs/vision.md it should match the curriculum

The README must match the main architecture pattern and code that exists today, not the code you expected to exist.

## First-Screen Rule

Assume the reader opens the example for the first time on GitHub. In the first 20-60 seconds they need answers to:
- What is this pattern?
- Why should I care?
- How do I run it?
- What do I get back if it works?

Because GitHub adds repository chrome above the README, avoid spending the first screen on long theory blocks or a large `What You'll Learn` list. Put value, run path, and expected payoff near the top.

## Recommended Pattern README Flow

Use this order by default for example READMEs:

```markdown
# Pattern NN: [Title]

> One-sentence value proposition.

Short positioning paragraph:
- where this pattern fits in the series
- what team/use case it belongs to
- what limitation it sets up for the next pattern

## Quick Start

Show the fastest runnable path first.

## What You Get Back

Show the response shape, output artifact, or visible success criteria.

## At a Glance

Compact table: agents, runtime, ports, endpoints, prerequisites, observability.

## The Problem

What breaks in the simpler approach? Why does this pattern exist?

## Architecture

Use Mermaid when the topology or flow is not obvious. This is the important part, we are focusing on the architecture and flow not the code.



## Key Concepts

Short bullets only. Keep the deep explanation lower in the doc.

## Implementation Walkthrough

Explain the important code in steps, with annotated snippets.
Do not explain the code that is not part of the example, just present the main idea and flow.

## What You Should See

Expected logs, traces, response shape, or runtime behavior.

## Verification

One or two concrete requests plus expected success and failure behavior.

```

You may merge `What You Get Back` and `At a Glance` when the example is very small, but do not move `Quick Start` far down the page unless the user explicitly wants a tutorial-first flow.

## README Quality Rules

- **GitHub-first**: treat the README like a landing page first and a reference document second.
- **Self-contained**: a developer should understand the pattern without opening five other files.
- **Use case consistency**: keep the crypto intelligence platform story and team evolution intact.
- **Progressive narrative**: explain what limitation motivates the next pattern.
- **Code-to-doc fidelity**: verify names, ports, env vars, response fields, validation, failure modes, and Docker UX against the implementation.
- **No time bombs**: avoid hardcoded years or other values that drift over time unless the code also hardcodes them.
- **No duplication**: do not explain the same concept twice at two different depths unless the second time adds new information.
- **Show payoff early**: include an output example, trace snippet, or success criteria near the top half of the page.
- **Keep code snippets selective**: show the parts that teach the architecture; do not dump full files.

## Fidelity Checklist

Before finalizing an example README, verify:
- the documented quick start matches the actual `docker compose` flow
- repo-root `.env` dependencies are stated explicitly when present
- optional shortcuts are labeled as optional
- provider selection instructions match shared config defaults
- endpoint names, response fields, and validation behavior match tests
- failure behavior matches the real implementation
- tracing and verbose logging are described accurately
- the transition to the next pattern is explicit and honest

## Mermaid Diagram Guidelines

- Use `graph TD` for architecture overviews
- Use `flowchart LR` for pipeline patterns
- Use `sequenceDiagram` for request/response or protocol flows
- Use `stateDiagram-v2` for stateful agent behavior
- No spaces in node IDs: use `camelCase` or `underscores`
- Wrap special characters in labels with double quotes
- Do not add custom colors or styles
- For multi-service patterns, show containers, networks, and protocols clearly

