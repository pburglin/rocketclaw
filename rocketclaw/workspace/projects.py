from __future__ import annotations

from pathlib import Path

from rocketclaw.workspace.manager import workspace_dir

ACTIVE_FILE = "ACTIVE_PROJECT.txt"


def set_active_project(name: str) -> Path:
    proj_root = workspace_dir() / "PROJECTS"
    proj_root.mkdir(parents=True, exist_ok=True)
    proj = proj_root / name
    proj.mkdir(parents=True, exist_ok=True)
    active = proj_root / ACTIVE_FILE
    active.write_text(name)
    return proj


def get_active_project() -> Path | None:
    proj_root = workspace_dir() / "PROJECTS"
    active = proj_root / ACTIVE_FILE
    if not active.exists():
        return None
    name = active.read_text().strip()
    if not name:
        return None
    return proj_root / name
