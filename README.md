# Agent Patterns Lab

Practical design patterns, protocols, and architectures for real-world AI agents.

A progressive, hands-on learning repository that takes you from a single LangGraph agent to a fully distributed, authenticated, cloud-deployed multi-agent system.

## Tech Stack

- **Python 3.14+** with **uv** for package and Python version management
- **LangGraph** for agent orchestration
- **FastAPI** for agent HTTP endpoints
- **Docker Compose** for local multi-container environments
- **LangSmith** for tracing and observability
- **Auth0** for OIDC-based agent authentication (Lesson 4+)
- **Azure Container Apps** for cloud deployment (Lesson 6+)
- **A2A / MCP** protocols for agent communication

## Curriculum

### Phase 1: Learning Agent Patterns (8 Lessons)

| # | Lesson | Key Concepts |
|---|--------|-------------|
| 1 | [Multi-Agent Single System](examples/01-multi-agent-single-system/) | LangGraph StateGraph, orchestrator pattern, LangSmith tracing |
| 2 | [Memory and External Services](examples/02-memory-and-external-services/) | MCP protocol, Supabase, persistent state, tool abstraction |
| 3 | [Distributed Agents Communication](examples/03-distributed-agents-communication/) | Separate containers, A2A protocol, Agent Cards |
| 4 | [Cross-Network Authentication](examples/04-cross-network-authentication/) | Auth0 OIDC, M2M tokens, JWT validation |
| 5 | [Agent Discovery](examples/05-agent-discovery/) | Registry patterns, Agent Cards, enterprise governance |
| 6 | [Azure Deployment](examples/06-azure-deployment/) | Bicep IaC, Container Apps, CI/CD pipeline |
| 7 | [UI and Observability](examples/07-ui-and-observability/) | Chat UI, LangSmith dashboard, OpenTelemetry |
| 8 | [Full Stack Integration](examples/08-full-stack-integration/) | All patterns combined, production reference architecture |

### Phase 2: Conversational Tutoring System (Planned)

Applies Phase 1 patterns to a real-world distributed system with cross-team agent collaboration. See [docs/phase2/README.md](docs/phase2/README.md).

## Quick Start

```bash
# Install uv (if not already installed)
# https://docs.astral.sh/uv/getting-started/installation/

# Clone and setup
git clone https://github.com/ksopyla/agent-patterns-lab.git
cd agent-patterns-lab
cp .env.example .env
# Fill in your API keys in .env

# Install all dependencies
make setup

# Run an example (e.g., lesson 1)
make example EX=01-multi-agent-single-system
```

## Project Structure

```
agent-patterns-lab/
├── examples/           # One folder per lesson, each self-contained
├── libs/common/        # Shared utilities (LLM config, tracing, logging)
├── docs/               # Curriculum, lessons, changelog
├── infra/              # Docker base images, Azure Bicep, Vercel config
├── ui/                 # Chat UI (Lesson 7+)
├── .github/            # CI/CD workflows, PR templates
└── .cursor/            # Cursor rules and skills for AI-assisted development
```

## Verbose / Debug Mode

Every example supports `VERBOSE=true` (set in `.env`) which logs:
- Agent reasoning steps with timestamps
- Tool call inputs/outputs
- Inter-agent message payloads
- LangSmith trace IDs for quick lookup

## Blog

Detailed write-ups for each lesson at [ai.ksopyla.com](https://ai.ksopyla.com).

## License

MIT
