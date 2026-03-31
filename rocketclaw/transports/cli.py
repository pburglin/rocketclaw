from __future__ import annotations

from dataclasses import dataclass

from rocketclaw.transports.base import InboundEvent, MessageEnvelope, OutboundMessage, SessionIdentity, Transport


@dataclass
class CliTransport(Transport):
    name: str = "cli"

    def normalize(self, event: InboundEvent) -> MessageEnvelope:
        raise NotImplementedError("CLI transport is interactive and does not normalize inbound events.")

    def send(self, message: OutboundMessage) -> None:
        raise NotImplementedError("CLI transport delegates output to the terminal UI.")
