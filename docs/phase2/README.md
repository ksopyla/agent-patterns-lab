# Phase 2: Conversational Tutoring System

## Status: Planned (after Phase 1 completion)

## Context

Building a distributed multi-agent system for conversational tutoring (voice-to-voice) in a global corporation. The system generates tailored roleplay scenarios based on learner profiles and assesses conversations across multiple dimensions.

This phase applies all patterns learned in Phase 1 to a real-world, cross-team architecture.

## Architecture

Two independent teams build and deploy their agent services separately, communicating via A2A protocol with Auth0 M2M authentication.

### Team A: Scenario Generation

| Agent | Responsibility |
|-------|---------------|
| Company Knowledge Collector | Gathers company-specific information, pain points, industry context |
| Learner Profile Builder/Updater | Builds and maintains learner profiles from conversation data |
| Scenario Generator | Creates roleplay scenarios tailored to company + learner context |
| Scenario Recommender | Selects the best scenario based on learning history and gaps |
| Feedback Orchestrator | After conversation, hands off to Team B for assessment via A2A |

### Team B: Assessment

| Agent | Responsibility |
|-------|---------------|
| Assessment Router | Receives handoff, routes to appropriate assessment agents |
| Finance Knowledge Checker | Evaluates domain-specific financial knowledge |
| English Correctness Feedback | Assesses language quality, grammar, vocabulary |
| Soft Skill Assessment | Evaluates communication style, empathy, negotiation |

New assessment agents can be added to Team B without any changes to Team A.

## Key Patterns from Phase 1

- **Lesson 3**: Distributed agents in separate containers (Team A vs Team B)
- **Lesson 4**: Auth0 M2M tokens for cross-team authentication
- **Lesson 5**: Agent discovery (Team B registers new assessment capabilities)
- **Lesson 2**: MCP for learner profile database access
- **Lesson 7**: Orchestrator pattern for scenario generation pipeline
- **Lesson 8**: Full stack integration with UI

## Open Questions / Reminders

- [ ] Define the exact learner profile schema (what data to extract from conversations)
- [ ] Decide on voice-to-voice integration (Azure Speech Services? Deepgram?)
- [ ] Design the assessment criteria format and how it maps to agent selection
- [ ] Plan the handoff protocol between Team A orchestrator and Team B router
- [ ] Consider: should Team B assessment results feed back into Team A's learner profile?
- [ ] Evaluate if a shared Supabase instance works or if each team needs their own data store
- [ ] Define SLA requirements for assessment turnaround time
- [ ] Plan for conversation transcript storage and privacy compliance
