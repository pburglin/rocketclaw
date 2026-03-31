from __future__ import annotations

from pathlib import Path
from typing import Iterable


def simple_search(paths: Iterable[Path], query: str) -> list[Path]:
    query_l = query.lower()
    matches: list[Path] = []
    for path in paths:
        try:
            if query_l in path.read_text().lower():
                matches.append(path)
        except OSError:
            continue
    return matches
