# RocketClaw

RocketClaw is a modular personal AI runtime. The default agent **Rocket** is a persistent assistant with identity and memory.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .[train]
rocketclaw --help
rocketclaw chat
```

## Quick demo (main features)

### 1) Basic Q&A

```bash
export OPENAI_API_KEY=your_key_here
rocketclaw ask "Summarize my workspace"
```

Expected: a single response from Rocket using the active workspace context.

### 2) Interactive chat

```bash
rocketclaw chat
```

Expected: REPL chat prompt. Type a message and receive a response. Use `/exit` to quit.

### 3) Memory search + show

```bash
rocketclaw memory search "project"
rocketclaw memory show .rocketclaw/workspaces/default/memory/semantic/example.md
```

Expected: search returns matching file paths; show prints the file content.

### 4) Workspace + agent switching

```bash
rocketclaw workspace list
rocketclaw workspace switch demo
rocketclaw agent active
```

Expected: lists workspaces, switches to `demo` (creating it if needed), and shows the active agent.

### 5) Tools + transports inventory

```bash
rocketclaw tool list
rocketclaw transport list
```

Expected: JSON lists of registered tools and transports (defaults: `cli`, `whatsapp`).

### 6) Durable task tracking

```bash
rocketclaw task add "follow up with Pedro"
rocketclaw task list
rocketclaw task complete task-0001
rocketclaw task list --status done
```

Expected: tasks are persisted under the active workspace `memory/tasks/` bucket and can be listed or completed later.

## Troubleshooting

- **`rocketclaw` not found**: ensure the venv is active and the package is installed (`pip install -e .[train]`).
- **Shell tool disabled**: set `ROCKETCLAW_ALLOW_SHELL=1` before running.
- **No memory results**: ensure `.rocketclaw` exists and that semantic/episodic files are present.
- **WhatsApp transport errors**: confirm provider credentials and webhook payload format for your provider.
- **Workspace issues**: run `rocketclaw workspace list` and `rocketclaw workspace switch <name>` to reset the active workspace.
## Docker

```bash
# Build

docker build -t rocketclaw:local .

# Run with mounted workspace
docker run --rm -it \
  -v "$PWD/.rocketclaw:/home/rocket/.rocketclaw" \
  rocketclaw:local

# Or with compose
docker compose up --build
```

## K8s (optional)

Basic deployment idea (single replica, scale as needed):

```bash
kubectl create namespace rocketclaw
kubectl -n rocketclaw create configmap rocketclaw-home --from-file=.rocketclaw
kubectl -n rocketclaw create deployment rocketclaw --image=rocketclaw:local \
  --dry-run=client -o yaml > rocketclaw-deploy.yaml
kubectl -n rocketclaw apply -f rocketclaw-deploy.yaml
kubectl -n rocketclaw scale deployment rocketclaw --replicas=2
```

Mount `.rocketclaw` as a volume and ensure each replica has its own persistent storage or a shared PVC if needed.

## CLI

- `rocketclaw ask "question"`
- `rocketclaw chat`
- `rocketclaw memory search <query>`
- `rocketclaw memory show <path>`
- `rocketclaw soul edit`
- `rocketclaw user edit`
- `rocketclaw project switch <name>`
- `rocketclaw workspace list`
- `rocketclaw workspace switch <name>`
- `rocketclaw agent active`
- `rocketclaw agent switch <name>`
- `rocketclaw skill list`
- `rocketclaw tool list`
- `rocketclaw transport list`
- `rocketclaw task list`
- `rocketclaw task add <title>`
- `rocketclaw task complete <task-id>`

## Workspace Layout

```
.rocketclaw/
  workspaces/
    default/
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

## Formats

- Config: JSON
- Context + memory: Markdown

## LLM Providers

RocketClaw supports multiple LLM providers with per-provider auth, priority order, smart routing, and cooldowns on errors.

Provider config is stored in `.rocketclaw/config/providers.json` (created by `rocketclaw` on first run). If the file is missing, RocketClaw falls back to environment variables like `ROCKETCLAW_MODEL`, `ROCKETCLAW_MODEL_PROVIDERS`, and `ROCKETCLAW_MODEL_COOLDOWN_SECONDS`.

## Skills

RocketClaw maintains an inventory of installed skills and ships with a basic set of common skills. Skills extend agent capabilities and tools.

## Default Tools

- filesystem
- memory_write
- memory_search
- http_fetch
- shell_command (gated by `ROCKETCLAW_ALLOW_SHELL=1`)
- task_manager (durable tasks persisted in `memory/tasks/`)

Default tool wiring is modular: `build_default_tools(...)` produces the built-in tool set, and `ToolRegistry.register_many(...)` can batch-register them into custom runtimes or tests.

## Transports

Transport discovery is registry-backed and powers `rocketclaw transport list`. Defaults are `cli` and `whatsapp`.

Built-in transport specs are also exposed through `default_transport_specs()` for custom composition, and WhatsApp outbound sends return provider metadata/results to make transport integrations easier to observe in tests and higher-level runtime code.

See `docs/architecture.md` for details.
