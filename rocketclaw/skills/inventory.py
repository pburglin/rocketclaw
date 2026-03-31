from __future__ import annotations

import json
from typing import Any

from rocketclaw.config.settings import SETTINGS, SKILLS_FILE, ensure_layout


def list_skills() -> list[str]:
    ensure_layout()
    path = SETTINGS.config_dir / SKILLS_FILE
    data = json.loads(path.read_text())
    return sorted(data.get("installed", []))


def add_skill(name: str) -> None:
    ensure_layout()
    path = SETTINGS.config_dir / SKILLS_FILE
    data: dict[str, Any] = json.loads(path.read_text())
    installed = set(data.get("installed", []))
    installed.add(name)
    data["installed"] = sorted(installed)
    path.write_text(json.dumps(data, indent=2))
