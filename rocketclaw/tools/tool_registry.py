from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable

import os

import httpx

from rocketclaw.memory.memory_store import MemoryStore
from rocketclaw.memory.retrieval import simple_search
from rocketclaw.memory.task_store import TaskStore


@dataclass
class Tool:
    name: str
    schema: dict[str, Any]
    permissions: list[str]
    handler: Callable[[dict[str, Any]], Any]


@dataclass
class ToolRegistry:
    tools: dict[str, Tool] = field(default_factory=dict)

    def register(self, tool: Tool) -> None:
        self.tools[tool.name] = tool

    def register_many(self, tools: Iterable[Tool]) -> None:
        for tool in tools:
            self.register(tool)

    def list(self) -> list[str]:
        return sorted(self.tools.keys())

    def execute(self, name: str, payload: dict[str, Any]) -> Any:
        if name not in self.tools:
            raise KeyError(f"Unknown tool: {name}")
        return self.tools[name].handler(payload)


def default_registry(
    memory_store: MemoryStore | None = None,
    memory_searcher: Callable[[Iterable[Path], str], Iterable[Path]] | None = None,
    http_get: Callable[[str, float], Any] | None = None,
    shell_runner: Callable[[str], str] | None = None,
) -> ToolRegistry:
    memory = memory_store or MemoryStore()
    searcher = memory_searcher or simple_search
    http_fetch = http_get or httpx.get
    run_shell = shell_runner or _run_shell

    registry = ToolRegistry()
    registry.register_many(
        build_default_tools(
            memory_store=memory,
            memory_searcher=searcher,
            http_get=http_fetch,
            shell_runner=run_shell,
        )
    )

    return registry


def build_default_tools(
    memory_store: MemoryStore,
    memory_searcher: Callable[[Iterable[Path], str], Iterable[Path]],
    http_get: Callable[[str, float], Any],
    shell_runner: Callable[[str], str],
) -> list[Tool]:
    task_store = TaskStore(memory=memory_store)
    return [
        create_filesystem_tool(),
        create_memory_write_tool(memory_store),
        create_memory_search_tool(memory_store, memory_searcher),
        create_http_fetch_tool(http_get),
        create_shell_command_tool(shell_runner),
        create_task_manager_tool(task_store),
    ]


def _run_shell(command: str) -> str:
    if os.getenv("ROCKETCLAW_ALLOW_SHELL") != "1":
        return "shell execution disabled"
    import subprocess

    result = subprocess.run(command, shell=True, check=False, capture_output=True, text=True)
    return result.stdout.strip() or result.stderr.strip()


def create_filesystem_tool() -> Tool:
    return Tool(
        name="filesystem",
        schema={"type": "object", "properties": {"path": {"type": "string"}}},
        permissions=["read"],
        handler=lambda payload: payload.get("path"),
    )


def create_memory_write_tool(memory: MemoryStore) -> Tool:
    return Tool(
        name="memory_write",
        schema={
            "type": "object",
            "properties": {"bucket": {"type": "string"}, "name": {"type": "string"}, "content": {"type": "string"}},
            "required": ["bucket", "name", "content"],
        },
        permissions=["write"],
        handler=lambda payload: str(
            memory.write(payload["bucket"], payload["name"], payload["content"])
        ),
    )


def create_memory_search_tool(
    memory: MemoryStore,
    searcher: Callable[[Iterable[Path], str], Iterable[Path]],
) -> Tool:
    return Tool(
        name="memory_search",
        schema={
            "type": "object",
            "properties": {"bucket": {"type": "string"}, "query": {"type": "string"}},
            "required": ["bucket", "query"],
        },
        permissions=["read"],
        handler=lambda payload: [
            path.read_text()
            for path in searcher(memory.list_bucket(payload["bucket"]), payload["query"])
        ],
    )


def create_http_fetch_tool(http_fetch: Callable[[str, float], Any]) -> Tool:
    return Tool(
        name="http_fetch",
        schema={"type": "object", "properties": {"url": {"type": "string"}}},
        permissions=["network"],
        handler=lambda payload: http_fetch(payload["url"], timeout=10).text,
    )


def create_shell_command_tool(run_shell: Callable[[str], str]) -> Tool:
    return Tool(
        name="shell_command",
        schema={"type": "object", "properties": {"command": {"type": "string"}}},
        permissions=["execute"],
        handler=lambda payload: run_shell(payload["command"]),
    )


def create_task_manager_tool(task_store: TaskStore) -> Tool:
    def handle(payload: dict[str, Any]) -> Any:
        action = str(payload.get("action", "add"))
        if action == "add":
            record = task_store.create(str(payload["task"]))
            return f"task recorded: {record.title} ({record.task_id})"
        if action == "list":
            status = payload.get("status")
            return [record.__dict__ for record in task_store.list(status=str(status) if status else None)]
        if action == "complete":
            record = task_store.complete(str(payload["task_id"]))
            return f"task completed: {record.title} ({record.task_id})"
        raise ValueError(f"Unknown task action: {action}")

    return Tool(
        name="task_manager",
        schema={
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["add", "list", "complete"]},
                "task": {"type": "string"},
                "task_id": {"type": "string"},
                "status": {"type": "string", "enum": ["open", "done"]},
            },
        },
        permissions=["write"],
        handler=handle,
    )
