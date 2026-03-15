---
name: documentation-writer
description: >-
  Produces LinkedIn-worthy, PDF-printable documentation with Mermaid diagrams.
  Use when creating README files, writing lesson documents, drafting blog posts
  for ai.ksopyla.com, creating LinkedIn post drafts, or any documentation request.
---

# Documentation Writer

## README Template

Every example folder README must follow this structure:

```markdown
# Lesson N: [Title]

> One-sentence summary of what this lesson teaches.

## What You'll Learn

- Takeaway 1
- Takeaway 2
- Takeaway 3

## The Problem

Describe the real-world scenario. Why does the previous lesson's approach fall short?

## Architecture

[Mermaid diagram here -- flowchart, sequence, or state diagram as appropriate]

## Key Concepts

Explain the theory. Use comparison tables for trade-offs.

## Implementation

### Step 1: [Description]
Annotated code snippet with explanation.

### Step 2: [Description]
Continue step by step.

## Running the Example

\`\`\`bash
# Prerequisites
cp .env.example .env
# Fill in API keys

# Run
docker compose up --build

# Test
curl http://localhost:8000/health
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d '{"input": "..."}'
\`\`\`

## Debug Walkthrough

Show the verbose output with annotations explaining what each agent is doing.

## Exercises

1. Extend the example in some way
2. Try a variation
3. Compare approaches

## Further Reading

- [Link to relevant spec or docs]
```

## Mermaid Diagram Guidelines

- Use `graph TD` for architecture overviews (top-down flow)
- Use `sequenceDiagram` for agent-to-agent communication flows
- Use `stateDiagram-v2` for agent state machines
- Use `flowchart LR` for pipeline patterns
- No spaces in node IDs: use `camelCase` or `underscores`
- Wrap special characters in labels with double quotes
- Do NOT add custom colors or styles -- let the theme handle it

## Lesson Document Format

Lessons in `docs/lessons/` are longer-form, PDF-printable documents. They expand on the README with:
- Deeper theory and background
- More diagrams showing internal agent architecture
- Comparison with alternative approaches
- "What the Agents Are Doing" section with annotated verbose output
- Screenshots of LangSmith traces (placeholder text until actual screenshots)

## LinkedIn Post Format

```
[Hook -- provocative question or surprising insight, 1-2 lines]

[3-4 lines of insight, what you learned building this]

[Key takeaway or actionable advice]

[CTA: link to blog post or repo]

#AIAgents #LangGraph #DistributedSystems #AgenticAI
```

Keep under 1300 characters. No emojis unless the user requests them.

## Blog Post Outline

For ai.ksopyla.com, produce an outline with:
1. Title (SEO-friendly, includes "AI agents" or "LangGraph")
2. Introduction (the problem, why it matters)
3. Sections matching the lesson structure
4. Code snippets (key parts, not full files)
5. Diagrams (embed Mermaid or export as images)
6. Conclusion with next steps
7. Link to the GitHub example
