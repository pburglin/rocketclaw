from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable

from rocketclaw.memory.memory_store import MemoryStore
from rocketclaw.memory.retrieval import simple_search
from rocketclaw.workspace.manager import get_active_agent
from rocketclaw.workspace.projects import get_active_project
from rocketclaw.workspace.soul import soul_path
from rocketclaw.workspace.user import user_path


@dataclass
class ContextSlice:
    name: str
    content: str


@dataclass
class ContextBuilder:
    memory: MemoryStore = field(default_factory=MemoryStore)
    searcher: Callable[[Iterable[Path], str], Iterable[Path]] = field(default_factory=lambda: simple_search)

    def build(self, conversation: str, semantic_query: str | None = None) -> list[ContextSlice]:
        slices: list[ContextSlice] = []
        slices.append(ContextSlice("SOUL", soul_path().read_text()))
        slices.append(ContextSlice("USER", user_path().read_text()))

        project = get_active_project()
        if project is not None:
            project_md = project / "PROJECT.md"
            if project_md.exists():
                slices.append(ContextSlice("PROJECT", project_md.read_text()))

        episodic_files = self.memory.list_bucket("episodic")
        if episodic_files:
            latest = sorted(episodic_files)[-1]
            slices.append(ContextSlice("EPISODIC", latest.read_text()))

        if semantic_query:
            semantic_files = self.memory.list_bucket("semantic")
            matches = list(self.searcher(semantic_files, semantic_query))
            if matches:
                content = "\n\n".join([m.read_text() for m in matches[:3]])
                slices.append(ContextSlice("SEMANTIC", content))

        slices.append(ContextSlice("CONVERSATION", conversation))
        return slices

    def build_for_subagent(self, task: str) -> list[ContextSlice]:
        slices: list[ContextSlice] = []
        slices.append(ContextSlice("SOUL", soul_path().read_text()))
        slices.append(ContextSlice("USER", user_path().read_text()))
        slices.append(ContextSlice("AGENT", f"Active agent: {get_active_agent()}"))
        slices.append(ContextSlice("TASK", task))
        return slices

    def debug_view(self, slices: Iterable[ContextSlice]) -> str:
        return "\n\n".join([f"## {s.name}\n{s.content}" for s in slices])
