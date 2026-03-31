from pathlib import Path

from rocketclaw.workspace.manager import workspace_dir


def user_path() -> Path:
    return workspace_dir() / "USER.md"
