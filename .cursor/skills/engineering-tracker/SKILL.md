---
name: engineering-tracker
description: >-
  Tracks major changes, maintains CHANGELOG.md with dates, motivation, and details.
  Use after completing a lesson, after major refactoring, after adding new dependencies,
  or when the user asks for a progress summary or changelog update.
---

# Engineering Tracker

## Purpose

Maintain a living record of the project's evolution in `docs/CHANGELOG.md`. This serves as:
- A learning journal for the author
- A reference for blog post writing
- A history of architectural decisions

## CHANGELOG.md Format

```markdown
# Changelog

All notable changes to this project are documented here.

## [YYYY-MM-DD] Lesson N: [Title]

### Added
- What was added and why

### Changed
- What was modified and the motivation

### Architecture Decisions
- Key decisions made and their rationale
- Alternatives considered and why they were rejected

### Dependencies
- New packages added with version and purpose
```

## When to Update

Update the changelog after:

1. **Completing a lesson**: summarize what was built, key decisions, new patterns introduced
2. **Major refactoring**: document what changed in `libs/common/` or shared infrastructure
3. **Adding dependencies**: note the package, version, and why it was needed
4. **Breaking changes**: if a change in one example affects others, document it clearly
5. **Infrastructure changes**: new Docker configurations, CI/CD updates, deployment changes

## Entry Structure

Each entry should answer:
- **What** changed (concrete files, features, configurations)
- **Why** it changed (motivation, problem being solved)
- **Impact** on other parts of the project (breaking changes, migration notes)

## How to Write Entries

1. Read the git diff or recent changes
2. Identify the major themes (new feature, refactor, fix, infrastructure)
3. Group changes by theme
4. Write concise but complete descriptions
5. Include architecture decision rationale when relevant

## Progress Summaries

When asked for a progress summary, produce:

```markdown
## Week of [date range]

### Completed
- Lesson N: [brief description]

### In Progress
- Lesson N: [what's done, what remains]

### Key Learnings
- Insight 1
- Insight 2

### Next Steps
- What to work on next
```
