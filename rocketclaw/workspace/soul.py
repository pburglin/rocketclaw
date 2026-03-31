from pathlib import Path

from rocketclaw.workspace.manager import workspace_dir


def soul_path() -> Path:
    return workspace_dir() / "SOUL.md"
