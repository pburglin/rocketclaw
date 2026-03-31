from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_HOME = Path.home() / ".rocketclaw"
CONFIG_FILE = "config.json"
SKILLS_FILE = "skills.json"
PROVIDERS_FILE = "providers.json"


@dataclass
class Settings:
    home: Path = DEFAULT_HOME

    @property
    def config_dir(self) -> Path:
        return self.home / "config"

    @property
    def workspaces_dir(self) -> Path:
        return self.home / "workspaces"


SETTINGS = Settings()


def ensure_layout(settings: Settings = SETTINGS) -> None:
    settings.config_dir.mkdir(parents=True, exist_ok=True)
    settings.workspaces_dir.mkdir(parents=True, exist_ok=True)

    config_path = settings.config_dir / CONFIG_FILE
    if not config_path.exists():
        config_path.write_text(
            json.dumps({"active_workspace": "default", "active_agent": "Rocket"}, indent=2)
        )

    config = load_config(settings)
    ensure_workspace_layout(config.get("active_workspace", "default"), settings=settings)

    skills_path = settings.config_dir / SKILLS_FILE
    if not skills_path.exists():
        skills_path.write_text(
            json.dumps(
                {
                    "installed": [
                        "filesystem",
                        "memory_write",
                        "memory_search",
                        "http_fetch",
                        "shell_command",
                        "task_manager",
                    ]
                },
                indent=2,
            )
        )

    providers_path = settings.config_dir / PROVIDERS_FILE
    if not providers_path.exists():
        providers_path.write_text(
            json.dumps(
                {
                    "cooldown_seconds": 60,
                    "providers": [
                        {"name": "local-echo", "type": "local-echo"},
                        {
                            "name": "openai-main",
                            "type": "openai_compatible",
                            "base_url": "https://api.openai.com/v1",
                            "model": "gpt-4o-mini",
                            "api_key_env": "OPENAI_API_KEY",
                            "timeout_seconds": 30,
                            "cooldown_seconds": 120
                        }
                    ]
                },
                indent=2,
            )
        )


def load_config(settings: Settings = SETTINGS) -> dict[str, Any]:
    config_path = settings.config_dir / CONFIG_FILE
    if not config_path.exists():
        ensure_layout(settings)
    return json.loads(config_path.read_text())


def save_config(data: dict[str, Any], settings: Settings = SETTINGS) -> None:
    config_path = settings.config_dir / CONFIG_FILE
    config_path.write_text(json.dumps(data, indent=2))


def ensure_workspace_layout(name: str, settings: Settings = SETTINGS) -> Path:
    base = settings.workspaces_dir / name
    workspace = base / "workspace"
    memory = base / "memory"

    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "PROJECTS").mkdir(parents=True, exist_ok=True)
    (memory / "episodic").mkdir(parents=True, exist_ok=True)
    (memory / "semantic").mkdir(parents=True, exist_ok=True)
    (memory / "procedural").mkdir(parents=True, exist_ok=True)
    (memory / "tasks").mkdir(parents=True, exist_ok=True)

    soul = workspace / "SOUL.md"
    user = workspace / "USER.md"
    agents = workspace / "AGENTS.md"

    if not soul.exists():
        soul.write_text("# SOUL\n\nRocket is your persistent AI assistant.\n")
    if not user.exists():
        user.write_text("# USER\n\nAdd user preferences here.\n")
    if not agents.exists():
        agents.write_text("# AGENTS\n\n- Rocket\n")

    return base
