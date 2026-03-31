from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from rocketclaw.workspace.manager import memory_dir


@dataclass
class MemoryStore:
    base: Path | None = None

    def init(self) -> None:
        if self.base is None:
            self.base = memory_dir()
        self.base.mkdir(parents=True, exist_ok=True)

    def write(self, bucket: str, name: str, content: str) -> Path:
        self.init()
        target = self.base / bucket / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        return target

    def append(self, bucket: str, name: str, content: str) -> Path:
        self.init()
        target = self.base / bucket / name
        target.parent.mkdir(parents=True, exist_ok=True)
        existing = target.read_text() if target.exists() else ""
        if existing and not existing.endswith("\n"):
            existing += "\n"
        target.write_text(existing + content)
        return target

    def read(self, bucket: str, name: str) -> str:
        self.init()
        target = self.base / bucket / name
        return target.read_text()

    def list_bucket(self, bucket: str) -> Iterable[Path]:
        self.init()
        target = self.base / bucket
        if not target.exists():
            return []
        return sorted(target.glob("*"))
