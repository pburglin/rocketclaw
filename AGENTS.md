# AGENTS.md - RocketClaw

## Overview

RocketClaw is a modular personal AI runtime. The default agent is **Rocket**.

## Structure

- `rocketclaw/core`: agent loop + context builder
- `rocketclaw/memory`: durable memory IO + retrieval
- `rocketclaw/tools`: tool registry and tool definitions
- `rocketclaw/transports`: transport abstraction + WhatsApp adapter
- `rocketclaw/interface`: CLI + REPL
- `docs/architecture.md`: system design

## Build / Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .[train]
rocketclaw --help
rocketclaw chat
```

## Tests

```bash
pytest
```

## Docker

Use a container to scope local directory access. Add a Dockerfile and run with a mounted `.rocketclaw` directory.

## Conventions

- Python 3.10+
- Pydantic models for envelopes and settings
- Prefer small, composable modules
- Explicit context order (SOUL → USER → PROJECT → episodic → semantic → conversation)
- Sub-agent decomposition for complex tasks; only minimal context per sub-agent
- JSON for config files; Markdown for context/memory
- Multi-provider LLM routing with auth, priorities, error-based fallback, cooldowns
- Skills system with installed-skill inventory and OOB common skills
- Avoid hidden network calls in core logic
