from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field


class SessionIdentity(BaseModel):
    channel: str
    user_id: str


class MessageEnvelope(BaseModel):
    text: str
    session: SessionIdentity
    metadata: dict[str, Any] = Field(default_factory=dict)


class OutboundMessage(BaseModel):
    text: str
    session: SessionIdentity


class InboundEvent(BaseModel):
    body: dict[str, Any]


class Transport:
    name: str = "base"

    def normalize(self, event: InboundEvent) -> MessageEnvelope:
        raise NotImplementedError

    def send(self, message: OutboundMessage) -> Any:
        raise NotImplementedError
