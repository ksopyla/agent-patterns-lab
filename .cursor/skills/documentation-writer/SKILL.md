---
name: documentation-writer
description: >-
  Produces professional, PDF-printable documentation with Mermaid diagrams.
  Use when creating pattern README files, drafting blog posts for ai.ksopyla.com,
  creating LinkedIn post drafts, or any documentation request.
---

# Documentation Writer

## Pattern README Template

Documentation is co-located with code -- each pattern has a comprehensive `README.md` inside its `examples/NN-name/` folder. The README is the single source of truth for each pattern's theory, architecture, implementation, and usage.

Every pattern README must follow this structure:

```markdown
# Pattern NN: [Name]

> One-sentence summary of the architectural challenge this pattern solves.

## Problem Statement

What architectural challenge does this pattern solve? Why does the previous
pattern's approach fall short for this new requirement? Ground it in the
crypto intelligence use case narrative.

## Architecture

Mermaid diagram of the system -- show containers, agent nodes, communication
protocols, and data flow. Use ASCII-art diagrams for in-terminal readability
alongside or instead of Mermaid when appropriate.

## Key Concepts

Bullet list of concepts introduced in this pattern. Each bullet should be
a concept name followed by a one-sentence explanation.

## When to Use / When NOT to Use

Decision criteria for applying this pattern in production:
- **Use when:** concrete scenarios where this pattern is the right choice
- **Avoid when:** scenarios where a simpler or different pattern is better
- Include trade-off comparison table if multiple approaches exist

## Prerequisites

Which patterns must be completed before this one. Link to their READMEs.

## Implementation Walkthrough

Step-by-step code walkthrough with key snippets. Each step should:
1. State what problem this step solves
2. Show the relevant code (annotated, not full files)
3. Explain design decisions and why alternatives were rejected

### Step 1: [Description]
### Step 2: [Description]
...

## Running the Example

\`\`\`bash
# Prerequisites
cp .env.example .env
# Fill in API keys

# Run
docker compose up --build

# Test
curl http://localhost:8000/health
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"input": "Research the Arbitrum crypto project"}'
\`\`\`

## What You Should See (Verbose Output)

Show the expected verbose/trace output with annotations explaining what each
agent is doing at each step. This section is critical for learning -- readers
should be able to compare their output to this reference.

## Exercises

2-3 extensions the reader can try, ordered by difficulty:
1. Small modification (add a field, change a parameter)
2. Medium extension (add an agent node, new tool)
3. Ambitious challenge (architectural change, new capability)

## Trade-offs & Discussion

Pros, cons, and alternatives. Real-world considerations:
- Performance implications
- Failure modes and recovery
- When to evolve to the next pattern
- Comparison with alternative approaches (table format preferred)

## Further Reading

- Links to LangGraph docs, protocol specs, relevant papers
- Links to prerequisite / next pattern READMEs
```

## README Content Guidelines

- **Use case consistency**: All examples use the crypto intelligence platform use case (Teams 1-3). Reference the specific team and agents relevant to the pattern.
- **Self-contained**: A reader should understand the pattern from the README alone, without reading `docs/curriculum.md` first.
- **Code snippets**: Show annotated key parts, not full files. Reference file paths so readers can find the full source.
- **Progressive narrative**: Each README should reference what changed from the previous pattern and why the new pattern is needed.
- **No redundant summaries**: The README replaces any separate lesson document. It should be comprehensive enough to serve as blog source material.

## Mermaid Diagram Guidelines

- Use `graph TD` for architecture overviews (top-down flow)
- Use `sequenceDiagram` for agent-to-agent communication flows
- Use `stateDiagram-v2` for agent state machines
- Use `flowchart LR` for pipeline patterns
- No spaces in node IDs: use `camelCase` or `underscores`
- Wrap special characters in labels with double quotes
- Do NOT add custom colors or styles -- let the theme handle it
- For multi-service architectures (Pattern 05+), show containers, networks, and protocols clearly

