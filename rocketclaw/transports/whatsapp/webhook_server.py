from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from rocketclaw.transports.base import InboundEvent, MessageEnvelope
from rocketclaw.transports.whatsapp.adapter import WhatsAppAdapter


@dataclass
class WebhookServer:
    adapter: WhatsAppAdapter

    def handle(self, payload: dict[str, Any], on_message: Callable[[MessageEnvelope], None]) -> None:
        event = InboundEvent(body=payload)
        try:
            envelope = self.adapter.normalize(event)
        except ValueError:
            return
        on_message(envelope)
