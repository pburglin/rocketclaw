from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from rocketclaw.transports.base import InboundEvent, MessageEnvelope, OutboundMessage, SessionIdentity, Transport
from rocketclaw.transports.whatsapp.provider_meta import WhatsAppProvider


@dataclass
class WhatsAppAdapter(Transport):
    name: str = "whatsapp"
    provider: WhatsAppProvider | None = None
    seen_ids: set[str] = field(default_factory=set)

    def normalize(self, event: InboundEvent) -> MessageEnvelope:
        body = event.body
        message_id = str(body.get("MessageSid") or body.get("message_id") or "")
        if message_id and message_id in self.seen_ids:
            raise ValueError("duplicate webhook")
        if message_id:
            self.seen_ids.add(message_id)

        text = str(body.get("Body") or body.get("text") or "")
        from_number = str(body.get("From") or body.get("from") or "")
        session = SessionIdentity(channel=self.name, user_id=from_number)
        return MessageEnvelope(text=text, session=session, metadata=body)

    def send(self, message: OutboundMessage) -> dict[str, Any]:
        if not self.provider:
            raise RuntimeError("WhatsApp provider not configured")
        return self.provider.send_message(message.session.user_id, message.text)
