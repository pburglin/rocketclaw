# RocketClaw Architecture

RocketClaw is a local-first personal AI runtime. The default agent **Rocket** is persistent and identity-driven.

## Layers

```
rocketclaw/
  core/
    agent_runtime.py
    context_builder.py
    planner.py
  engine/
    model_provider.py
    sub_agents.py
  memory/
    memory_store.py
    retrieval.py
  tools/
    tool_registry.py
  transports/
    base.py
    cli.py
    registry.py
    whatsapp/
  interface/
    cli.py
    terminal_ui.py
  workspace/
    soul.py
    user.py
    projects.py
  config/
    settings.py
  observability/
    logging.py
```

## Responsibilities

- **core/**: agent loop, context assembly, tool orchestration.
- **engine/**: LLM provider abstraction (local + hosted) + sub-agent decomposition.
- **memory/**: durable identity and episodic/semantic/procedural/project memory.
- **tools/**: pluggable tool system with schemas/permissions.
- **transports/**: transport abstraction with registries plus WhatsApp + CLI adapters.
- **interface/**: CLI, REPL, and TUI hooks.
- **workspace/**: multi-workspace support, SOUL.md/USER.md/AGENTS.md + project switch.

## Context Order

1. SOUL.md
2. USER.md
3. PROJECT.md (if active)
4. episodic summary
5. semantic retrieval
6. current conversation

Context is inspectable using `rocketclaw memory show` and `rocketclaw memory search`.
ContextBuilder accepts an injectable semantic search function to keep retrieval modular and testable.

## Multi-Workspace, Agents, and Sub-Agents

- **Workspaces**: multiple isolated workspaces, each with its own SOUL/USER/AGENTS/PROJECTS and memory buckets.
- **Agents**: multiple persistent agents per workspace (default: Rocket).
- **Sub-agents**: the engine decomposes complex tasks into sub-agent runs. Each sub-agent receives only the minimal context needed to complete its assigned task.

## File Formats

- **Config**: JSON files for machine-friendly configuration and portability.
- **Context/Memory**: Markdown files for human review, version control, and easy editing.

## Multi-Provider LLM Routing

RocketClaw supports multiple LLM providers configured by the user with:

- per-provider auth setup
- user-defined priority order
- smart routing based on error signals (rate limits, auth failures, provider errors)
- cooldown windows to avoid rapid retry loops

The engine should degrade gracefully to the next provider when errors exceed thresholds.

## Skills System

RocketClaw maintains an inventory of installed skills that extend agents and tools. Requirements:

- local inventory of installed skills
- discover/create/improve skills
- ships OOB with a basic set of common skills
- skills surface as tools/agents via the tool registry

Tool registries can be constructed with injected dependencies (memory store, memory searcher, HTTP client, shell runner) to keep tests isolated and improve modularity.
Tool factories (filesystem, memory, HTTP, shell, task manager) keep default registry wiring small and testable.
`build_default_tools(...)` returns the default tool set as composable `Tool` instances, and `ToolRegistry.register_many(...)` supports batch registration for custom runtimes.
## Transport Model

Every inbound message becomes a `MessageEnvelope`. The runtime is transport-agnostic.

```
InboundEvent -> MessageEnvelope -> AgentRuntime -> OutboundMessage -> Transport
```

Transports are registered via `TransportRegistry` for consistent CLI listing and future transport discovery.
`default_transport_specs()` exposes the built-in transport specs for reuse, while `TransportRegistry.register_many(...)` makes extension and test setup simpler.

## WhatsApp

Webhook ingestion uses `WebhookServer`, with idempotent handling via message-id caches. Provider abstraction supports Twilio or other APIs, and outbound adapter sends return provider responses for easier observability and testing.

## Tasks

The `task_manager` tool is backed by a durable `TaskStore` that writes Markdown records into the active workspace `memory/tasks/` bucket. Tasks can be added, listed, and marked done via the tool registry or the CLI `rocketclaw task ...` commands.

## Testing

Tests validate memory IO and retrieval, durable task persistence, episodic logging, transport normalization and de-duplication, outbound send wiring and provider passthrough, CLI transport behavior, context assembly, tool registry execution, batch registry wiring, and webhook parsing.
