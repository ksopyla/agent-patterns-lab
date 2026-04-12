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
- `docker-compose.yml` (shared `infra/docker/base/Dockerfile.agent` via build args), `endpoints.http`
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

> One-sentence value proposition -- mention the key pattern(s) introduced.

Short positioning paragraph:
- where this pattern fits in the series
- what team/use case it belongs to
- what limitation it sets up for the next pattern

## Quick Start

Fastest runnable path: .env setup, docker compose, curl. Include the
verification request here so there's no need for a separate Verification section.

## What You Get Back

Response shape or visible success criteria.

## At a Glance

Compact table: agents, graph topology, runtime, ports, data sources, observability.

## The Problem

2-4 sentences. State the limitation(s) of the previous pattern. No comparison
tables unless the comparison genuinely adds value that prose cannot.

## Architecture

Mermaid diagram + a paragraph explaining WHY it's structured this way (e.g. why
two containers, why parallel), not just describing what exists.

## Key Concepts

4 bullets max, one line each, em-dashes not colons. If it reads like AI marketing
copy, rewrite it shorter.

## Implementation Walkthrough

Link to source files so the reader can jump directly. Show code only when it's
the actual working snippet that teaches the architecture (e.g. the MCP tool
definition). For everything else, reference the file and explain the idea in
prose. Never show pseudo-code or comment-only code blocks.

## Connect Your MCP Client / Integration
(if applicable -- combine all client tools into one section, CLI first, GUI last)

## Local Development

uv sync, test, lint commands.

## Exercises

2 items max. One simple extension, one architectural extension. One sentence each.

## Trade-offs

Table of advantages vs. limitations. End with the bridge to the next pattern.

## Further Reading

Only link docs for technologies introduced in this pattern.
```

**Sections to skip:**

- **What You Should See** -- skip if Quick Start already shows expected output
- **Verification** -- never duplicate Quick Start with the same curl commands

## README Quality Rules

- **GitHub-first**: treat the README like a landing page, not a reference manual.
- **Self-contained**: a developer should understand the pattern without opening five other files.
- **Use case consistency**: keep the crypto intelligence platform story and team evolution intact.
- **Progressive narrative**: explain what limitation motivates the next pattern.
- **Code-to-doc fidelity**: verify names, ports, env vars, response fields, validation, failure modes, and Docker UX against the implementation.
- **No time bombs**: avoid hardcoded years or other values that drift over time unless the code also hardcodes them.
- **Say it once**: if a concept appears in Quick Start, don't repeat it in a Verification section. Every section must add information that no other section covers.
- **Show payoff early**: include an output example or success criteria near the top half of the page.

## Writing Style Rules

- **Reference files, don't duplicate code**: link to source files (`[file.py](path)`) so readers can jump directly. Only inline a code snippet when it's the actual working code and it teaches the architecture. Never show pseudo-code, comment-only blocks, or partial extracts that don't compile.
- **Architecture explanation helps, not just describes**: when mentioning infrastructure (containers, ports, networks), explain WHY it's structured that way, not just WHAT exists.
- **Key Concepts are tight**: 4 bullets max. One line each with em-dash separators. Cut any bullet that restates the architecture diagram.
- **The Problem is concise**: 2-4 sentences stating the limitation. No comparison tables unless truly needed.
- **Exercises are short**: 2 items max. One sentence each. One simple extension, one architectural.
- **Further Reading is scoped**: only link docs for technologies introduced by this specific pattern.
- **Integration guides are combined**: don't split Claude Code / Cursor / Claude Desktop into separate sections. One section, multiple examples, developer-workflow order (CLI tools first, GUI apps last).
- **No AI tone**: avoid marketing-speak, over-explanation, and restating the obvious. If a sentence doesn't add information, delete it.

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

