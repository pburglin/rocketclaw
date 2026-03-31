from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

from rocketclaw.memory.memory_store import MemoryStore


@dataclass
class TaskRecord:
    task_id: str
    title: str
    status: str
    created_at: str
    completed_at: str | None = None


@dataclass
class TaskStore:
    memory: MemoryStore

    def create(self, title: str) -> TaskRecord:
        task_id = self._next_task_id()
        created_at = _timestamp()
        record = TaskRecord(
            task_id=task_id,
            title=title.strip(),
            status="open",
            created_at=created_at,
            completed_at=None,
        )
        self.memory.write("tasks", f"{task_id}.md", self._serialize(record))
        return record

    def list(self, status: str | None = None) -> list[TaskRecord]:
        records = [self._read_task(path) for path in self.memory.list_bucket("tasks") if path.suffix == ".md"]
        records.sort(key=lambda record: record.task_id)
        if status is None:
            return records
        return [record for record in records if record.status == status]

    def complete(self, task_id: str) -> TaskRecord:
        record = self.get(task_id)
        if record.status != "done":
            record.status = "done"
            record.completed_at = _timestamp()
            self.memory.write("tasks", f"{record.task_id}.md", self._serialize(record))
        return record

    def get(self, task_id: str) -> TaskRecord:
        normalized = self._normalize_task_id(task_id)
        path = self._task_path(normalized)
        if not path.exists():
            raise KeyError(f"Unknown task: {task_id}")
        return self._read_task(path)

    def _next_task_id(self) -> str:
        existing = [self._normalize_task_id(path.stem) for path in self.memory.list_bucket("tasks") if path.suffix == ".md"]
        if not existing:
            return "task-0001"
        highest = max(int(task_id.split("-")[-1]) for task_id in existing)
        return f"task-{highest + 1:04d}"

    def _task_path(self, task_id: str) -> Path:
        self.memory.init()
        assert self.memory.base is not None
        return self.memory.base / "tasks" / f"{task_id}.md"

    def _read_task(self, path: Path) -> TaskRecord:
        lines = path.read_text().splitlines()
        if len(lines) < 5:
            raise ValueError(f"Malformed task file: {path}")
        values: dict[str, str] = {}
        for line in lines[1:5]:
            key, _, value = line.partition(":")
            values[key.strip()] = value.strip() or None
        return TaskRecord(
            task_id=values["id"],
            title=values["title"],
            status=values["status"],
            created_at=values["created_at"],
            completed_at=values.get("completed_at") or None,
        )

    def _serialize(self, record: TaskRecord) -> str:
        completed = record.completed_at or ""
        return (
            f"# Task {record.task_id}\n"
            f"id: {record.task_id}\n"
            f"title: {record.title}\n"
            f"status: {record.status}\n"
            f"created_at: {record.created_at}\n"
            f"completed_at: {completed}\n"
        )

    def _normalize_task_id(self, task_id: str) -> str:
        task_id = task_id.strip()
        if task_id.startswith("task-"):
            return task_id
        if task_id.isdigit():
            return f"task-{int(task_id):04d}"
        return task_id


def _timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")
