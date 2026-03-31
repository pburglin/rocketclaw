# RocketClaw — Requirements

**Source:** User-provided spec message (2026-03-17).

## 1. Project Overview
RocketClaw is a modular **personal AI agent runtime**. The default built-in agent is **Rocket**, a persistent personal assistant that maintains identity, memory, and long-term user context.

**Primary goals:**
1. CLI-first interface
2. Messaging integration (WhatsApp first)
3. Persistent memory
4. Extensible agent system
5. Modular architecture
6. Local-first operation
7. Transparent context and identity files

RocketClaw should feel like a **personal AI operating system**.

## 2. Core Architecture
### 2.1 Layers
```
rocketclaw/
  core/
    agent_runtime
    context_builder
    planner
  engine/
    model_provider
  memory/
    memory_store
    retrieval
  tools/
    tool_registry
  transports/
    cli
    whatsapp
  interface/
    terminal_ui
  workspace/
    soul
    user
    projects
  config/
  observability/
```

### 2.2 Additional core requirements
- Support **multiple workspaces, agents, and sub-agents**.
- Engine should decompose complex tasks into sub-agents, each receiving **minimal required context**.
- **Config files must be JSON**; **context/memory files must be Markdown** for easy review and version control.

### 2.2 Responsibilities
- **Core / Intelligence**: agent loop, tool orchestration, reasoning, context construction
- **Engine**: LLM provider abstraction, local + hosted models
- **Memory**: identity, user knowledge, episodic history, semantic knowledge, project memory
- **Tools**: pluggable tool system
- **Transport**: messaging adapters
- **Interface**: CLI and terminal UI

## 3. CLI Requirements
Command: `rocketclaw`

Supported commands:
- `rocketclaw ask "question"`
- `rocketclaw chat`
- `rocketclaw memory search`
- `rocketclaw memory show`
- `rocketclaw soul edit`
- `rocketclaw user edit`
- `rocketclaw project switch`
- `rocketclaw tool list`
- `rocketclaw transport list`

Interactive mode: `rocketclaw chat`

Features:
- REPL chat
- slash commands
- tool activity display
- memory recall indicators
- session persistence

Recommended stack:
- Python
- Typer or Click
- Textual or prompt_toolkit

## 4. Extensible Transport System
All channels use common abstraction:
- `Transport`
- `MessageEnvelope`
- `InboundEvent`
- `OutboundMessage`
- `SessionIdentity`

Requirements:
- Every input channel converts to shared format
- Agent runtime must be transport-agnostic

Future transports: Telegram, Discord, SMS, Email, Web chat, Voice

## 5. WhatsApp Integration
First-class transport:
```
transports/
  whatsapp/
    adapter.py
    webhook_server.py
    provider_meta.py
    provider_twilio.py
```

Requirements:
- webhook ingestion
- outbound messaging
- session mapping by phone number
- idempotent webhook handling
- provider abstraction

Inbound flow:
Webhook → Transport Adapter → MessageEnvelope → Agent Runtime → Response → WhatsApp API

Support:
- text
- media metadata
- delivery status

## 6. Memory System
Workspace layout:
```
.rocketclaw/
  workspace/
    SOUL.md
    USER.md
    AGENTS.md
    PROJECTS/
  memory/
    episodic/
    semantic/
    procedural/
    tasks/
```

SOUL.md defines Rocket’s identity/personality/mission/behavior rules.
USER.md stores user preferences, facts, goals, relationships.

Memory types:
- Episodic (session summaries)
- Semantic (durable facts)
- Procedural (workflows)
- Project memory (scoped to active project)

## 7. Context Building Order
Context assembly order:
1. SOUL.md
2. USER.md
3. PROJECT.md (if active)
4. episodic summary
5. semantic retrieval
6. current conversation

Context builder must expose debug tools to inspect injected context.

## 8. Tools System
Pluggable tool registry. Example tools:
- filesystem
- memory_write
- memory_search
- http_fetch
- shell_command
- task_manager

Every tool defines:
- name
- schema
- permissions
- execution handler

### 8.1 Skills Support
RocketClaw must keep an inventory of installed skills to extend agent capabilities and tools. It must:
- find/create new skills
- improve existing skills
- ship OOB with a basic list of common skills

## 9. Repository Structure
```
rocketclaw/
  rocketclaw/
    core/
    engine/
    memory/
    tools/
    transports/
    interface/
  tests/
  examples/
  docs/
```

Must include:
- README.md
- AGENTS.md
- architecture.md

AGENTS.md must explain:
- how the codebase works
- build commands
- test commands
- coding conventions

## 9.1 Docker
Provide steps to run RocketClaw in a Docker container to control local directory access.

## 10. Testing
Add automated tests for:
- memory loading
- transport normalization
- CLI commands
- context assembly
- tool execution
- webhook parsing

## 11. Deliverables (Implementation Order)
1. architecture document
2. repository scaffold
3. CLI implementation
4. memory system
5. context builder
6. tools registry
7. WhatsApp transport
8. tests
9. example workspace

## 12. Quality Requirements
Code must be:
- clean
- modular
- testable
- extensible

Avoid unnecessary complexity. Prefer clear architecture over cleverness.

## 13. Workflow Instructions
Implementation loop:
1. Analyze repo
2. Short architecture plan
3. Implement code incrementally
4. Run tests/validation
5. Fix errors
6. Continue until milestone complete

If repo empty: initialize project, create architecture.md, repo structure, initial CLI.

## 14. Additional Instruction
If information is missing, infer reasonable defaults. Break large tasks into multiple commits/patches.
