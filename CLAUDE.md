# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Agent Engine is a Domain-Driven Design (DDD) based agent orchestration system that manages AI agent sessions and task dispatching. It supports multiple AI providers (Claude, Gemini) and uses PostgreSQL for persistence and event-driven communication.

## Development Commands

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Run specific test file
uv run pytest tests/unit/orchestration/domain/aggregates/test_dispatch_job.py

# Run tests with verbose output
uv run pytest -v

# Run tests with coverage
uv run pytest --cov=src/agent_engine

# Type checking
uv run basedpyright

# CLI commands
uv run agent-engine --help
uv run agent-engine start-workflow "Build a REST API"
uv run agent-engine tick          # Single event loop tick
uv run agent-engine listen        # Long-running event listener
uv run agent-engine execute-session --help
```

## Architecture

### Bounded Contexts

The system follows DDD with two bounded contexts, each with its own container:

**1. Orchestration Context** (`src/agent_engine/orchestration/`)
- Manages task dispatching and job lifecycle
- Handles domain events (TaskReadyEvent, TaskReviewRequestedEvent)
- Uses PostgreSQL LISTEN/NOTIFY for event-driven communication
- Key aggregates: `DispatchJob`
- Key use cases: `HandleDispatchableTaskEvent`, `StartInitialWorkflow`, `RunEventLoopTick`

**2. Execution Context** (`src/agent_engine/execution/`)
- Manages AI agent sessions and gateway routing
- Supports Claude and Gemini providers via `AgentGatewayRouter`
- Key aggregates: `AgentSession`
- Key use case: `ExecuteAgentSession`

### Dependency Injection

Uses `dependency-injector` library with a composition root in `shared/container.py`:
- `ApplicationContainer` assembles both bounded contexts
- `bootstrap()` function initializes the container with settings
- Each context has its own `Container` class

### SOP System (Standard Operating Procedures)

SOPs are Markdown files in `src/agent_engine/sops/` with YAML frontmatter:
- Naming convention: `{planning_level}_{status}.md` (e.g., `atomic_ready.md`)
- Frontmatter defines: `name`, `description`, `tools`, `model` (fast/pro)
- `LocalFileSopRepository` loads SOPs and builds system prompts

### Code Generation

The project uses a `codegen.yaml` blueprint for DDD code generation:
- `mcp_codegen_tree` - View blueprint structure
- `mcp_codegen_get` - Query values by path
- `mcp_codegen_set` - Set/update values
- `mcp_codegen_build` - Generate Python code from blueprint

### Domain Events

- Events are broadcast via PostgreSQL NOTIFY
- `PgNotifyEventListener` listens on configured channel
- Events include: `TaskReadyEvent`, `TaskReviewRequestedEvent`
- Each event carries `project_id`, `task_id`, `planning_level`, `status`

### Configuration

Configuration via environment variables (loaded from `~/.agent-engine/.env` or local `.env`):
- `DATABASE_URL` - PostgreSQL connection string for agent engine
- `TASK_GRAPH_DATABASE_URL` - PostgreSQL connection string for task graph
- `AGENT_PROVIDER` - Default provider (`claude` or `gemini`, default: `gemini`)
- `EVENT_BUS_CHANNEL` - PostgreSQL NOTIFY channel (default: `domain_events`)
- `PROJECT_ID` - Current project identifier
- `PROJECT_ROOT` - Root directory of the project

## Key Patterns

### Port/Adapter Pattern
- Ports define interfaces in `domain/ports/`
- Adapters implement interfaces in `infrastructure/adapters/`
- Example: `AgentGateway` (port) → `ClaudeAgentGateway`, `GeminiAgentGateway` (adapters)

### Repository Pattern
- Repository interfaces in `domain/ports/`
- SQLAlchemy implementations in `infrastructure/repositories/`
- Use async session factory for database operations

### Use Case Pattern
- Use cases are command handlers in `application/use_cases/`
- Dependencies injected via constructor
- Return typed result objects

### Value Objects
- Immutable, validated domain values
- Located in `shared/domain/value_objects/` and context-specific `domain/value_objects/`
- Implement `create()`, `reconstitute()`, `serialize()`, `__str__()` methods