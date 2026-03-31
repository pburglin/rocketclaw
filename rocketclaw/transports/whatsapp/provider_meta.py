from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class ProviderMeta:
    name: str
    base_url: str


class WhatsAppProvider(Protocol):
    meta: ProviderMeta

    def send_message(self, to_number: str, body: str) -> dict:
        ...
