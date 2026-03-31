from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable

from rocketclaw.transports.base import Transport
from rocketclaw.transports.cli import CliTransport
from rocketclaw.transports.whatsapp.adapter import WhatsAppAdapter


@dataclass
class TransportSpec:
    name: str
    factory: Callable[[], Transport]


@dataclass
class TransportRegistry:
    transports: dict[str, TransportSpec] = field(default_factory=dict)

    def register(self, spec: TransportSpec) -> None:
        self.transports[spec.name] = spec

    def register_many(self, specs: Iterable[TransportSpec]) -> None:
        for spec in specs:
            self.register(spec)

    def list(self) -> list[str]:
        return sorted(self.transports.keys())

    def create(self, name: str) -> Transport:
        if name not in self.transports:
            raise KeyError(f"Unknown transport: {name}")
        return self.transports[name].factory()


def default_transport_registry() -> TransportRegistry:
    registry = TransportRegistry()
    registry.register_many(default_transport_specs())
    return registry


def default_transport_specs() -> list[TransportSpec]:
    return [
        TransportSpec(name="cli", factory=CliTransport),
        TransportSpec(name="whatsapp", factory=WhatsAppAdapter),
    ]
