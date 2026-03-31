from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich import print as rprint

from rocketclaw.config.settings import ensure_layout
from rocketclaw.core.agent_runtime import AgentRuntime
from rocketclaw.core.context_builder import ContextBuilder
from rocketclaw.engine.model_provider import from_config
from rocketclaw.interface.terminal_ui import TerminalUI
from rocketclaw.memory.memory_store import MemoryStore
from rocketclaw.memory.task_store import TaskStore
from rocketclaw.memory.retrieval import simple_search
from rocketclaw.tools.tool_registry import default_registry
from rocketclaw.transports.base import MessageEnvelope, SessionIdentity
from rocketclaw.transports.registry import default_transport_registry
from rocketclaw.workspace.manager import (
    get_active_agent,
    get_active_workspace,
    list_workspaces,
    set_active_agent,
    set_active_workspace,
)
from rocketclaw.workspace.projects import get_active_project, set_active_project
from rocketclaw.workspace.soul import soul_path
from rocketclaw.workspace.user import user_path
from rocketclaw.skills.inventory import add_skill, list_skills

app = typer.Typer(no_args_is_help=True)


@app.command("skill")
def skill_cmd(
    action: str = typer.Argument("list", help="list|add"),
    name: str = typer.Argument("", help="Skill name to add"),
) -> None:
    """Manage skills inventory."""
    if action == "list":
        skills = list_skills()
        if skills:
            rprint(f"Installed skills: {skills}")
        else:
            rprint("No skills installed.")
        return
    if action == "add":
        if not name:
            raise typer.BadParameter("Skill name required")
        add_skill(name)
        rprint(f"Skill '{name}' added.")
        return
    raise typer.BadParameter("Unknown action")


@app.command()
def ask(question: str) -> None:
    """Ask Rocket a single question."""
    ensure_layout()
    runtime = AgentRuntime(model=from_config(), tools=default_registry())
    envelope = MessageEnvelope(text=question, session=SessionIdentity(channel="cli", user_id="local"))
    reply = runtime.handle(envelope)
    rprint(reply.text)


@app.command()
def chat() -> None:
    """Interactive REPL chat."""
    ensure_layout()
    ui = TerminalUI()
    runtime = AgentRuntime(model=from_config(), tools=default_registry(), context_builder=ContextBuilder())
    ui.print(f"RocketClaw chat (workspace: {get_active_workspace()}). Type /exit to quit.")
    while True:
        text = ui.prompt()
        if text.strip() in {"/exit", "/quit"}:
            break
        if text.startswith("/"):
            ui.print(f"Unknown command: {text}")
            continue
        envelope = MessageEnvelope(text=text, session=SessionIdentity(channel="cli", user_id="local"))
        reply = runtime.handle(envelope)
        ui.print(reply.text)


@app.command("memory")
def memory_cmd(
    action: str = typer.Argument(..., help="search|show"),
    value: str = typer.Argument(...),
) -> None:
    store = MemoryStore()
    if action == "search":
        files = store.list_bucket("semantic")
        matches = simple_search(files, value)
        for path in matches:
            rprint(str(path))
        return
    if action == "show":
        target = Path(value)
        if not target.exists():
            raise typer.BadParameter("File not found")
        rprint(target.read_text())
        return
    raise typer.BadParameter("Unknown action")


@app.command()
def soul(action: str = typer.Argument("edit")) -> None:
    if action != "edit":
        raise typer.BadParameter("Only edit supported")
    path = soul_path()
    rprint(path.read_text())
    rprint(f"Edit at: {path}")


@app.command()
def user(action: str = typer.Argument("edit")) -> None:
    if action != "edit":
        raise typer.BadParameter("Only edit supported")
    path = user_path()
    rprint(path.read_text())
    rprint(f"Edit at: {path}")


@app.command("project")
def project_switch(action: str = typer.Argument("switch"), name: str = typer.Argument(...)) -> None:
    if action != "switch":
        raise typer.BadParameter("Only switch supported")
    path = set_active_project(name)
    rprint(f"Active project: {path}")


@app.command("workspace")
def workspace_cmd(action: str = typer.Argument("list"), name: Optional[str] = None) -> None:
    if action == "list":
        rprint(json.dumps(list_workspaces(), indent=2))
        return
    if action == "switch":
        if not name:
            raise typer.BadParameter("Workspace name required")
        path = set_active_workspace(name)
        rprint(f"Active workspace: {path}")
        return
    raise typer.BadParameter("Unknown action")


@app.command("agent")
def agent_cmd(action: str = typer.Argument("active"), name: Optional[str] = None) -> None:
    if action == "active":
        rprint(get_active_agent())
        return
    if action == "switch":
        if not name:
            raise typer.BadParameter("Agent name required")
        set_active_agent(name)
        rprint(f"Active agent: {name}")
        return
    raise typer.BadParameter("Unknown action")


@app.command("tool")
def tool_list(action: str = typer.Argument("list")) -> None:
    if action != "list":
        raise typer.BadParameter("Only list supported")
    registry = default_registry()
    rprint(json.dumps(registry.list(), indent=2))


@app.command("transport")
def transport_list(action: str = typer.Argument("list")) -> None:
    if action != "list":
        raise typer.BadParameter("Only list supported")
    registry = default_transport_registry()
    rprint(json.dumps(registry.list(), indent=2))


@app.command("task")
def task_cmd(
    action: str = typer.Argument("list", help="list|add|complete"),
    value: Optional[str] = typer.Argument(None),
    status: Optional[str] = typer.Option(None, "--status", help="Filter task list by status"),
) -> None:
    store = TaskStore(memory=MemoryStore())
    if action == "list":
        tasks = [record.__dict__ for record in store.list(status=status)]
        rprint(json.dumps(tasks, indent=2))
        return
    if action == "add":
        if not value:
            raise typer.BadParameter("Task title required")
        record = store.create(value)
        rprint(f"Task added: {record.task_id} {record.title}")
        return
    if action == "complete":
        if not value:
            raise typer.BadParameter("Task id required")
        record = store.complete(value)
        rprint(f"Task completed: {record.task_id} {record.title}")
        return
    raise typer.BadParameter("Unknown action")
