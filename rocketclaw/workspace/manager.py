from __future__ import annotations

from pathlib import Path
from typing import Any

from rocketclaw.config.settings import SETTINGS, ensure_layout, load_config, save_config, ensure_workspace_layout


def get_active_workspace() -> str:
    ensure_layout()
    config = load_config()
    return config.get("active_workspace", "default")


def set_active_workspace(name: str) -> Path:
    ensure_layout()
    ensure_workspace_layout(name)
    config = load_config()
    config["active_workspace"] = name
    save_config(config)
    return SETTINGS.workspaces_dir / name


def list_workspaces() -> list[str]:
    ensure_layout()
    return sorted([p.name for p in SETTINGS.workspaces_dir.iterdir() if p.is_dir()])


def get_active_agent() -> str:
    ensure_layout()
    config = load_config()
    return config.get("active_agent", "Rocket")


def set_active_agent(name: str) -> None:
    ensure_layout()
    config = load_config()
    config["active_agent"] = name
    save_config(config)


def workspace_root(name: str | None = None) -> Path:
    ensure_layout()
    workspace = name or get_active_workspace()
    return SETTINGS.workspaces_dir / workspace


def workspace_dir(name: str | None = None) -> Path:
    return workspace_root(name) / "workspace"


def memory_dir(name: str | None = None) -> Path:
    return workspace_root(name) / "memory"
