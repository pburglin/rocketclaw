from dataclasses import dataclass

from rocketclaw.transports.base import InboundEvent, MessageEnvelope, OutboundMessage, SessionIdentity
from rocketclaw.transports.registry import (
    TransportRegistry,
    TransportSpec,
    default_transport_registry,
    default_transport_specs,
)
from rocketclaw.transports.whatsapp.adapter import WhatsAppAdapter
from rocketclaw.transports.whatsapp.provider_twilio import TwilioProvider
from rocketclaw.transports.whatsapp.webhook_server import WebhookServer
from rocketclaw.transports.cli import CliTransport


def test_whatsapp_normalize():
    adapter = WhatsAppAdapter()
    event = InboundEvent(body={"Body": "hi", "From": "+1555", "MessageSid": "abc"})
    envelope = adapter.normalize(event)
    assert envelope.text == "hi"
    assert envelope.session.user_id == "+1555"


def test_whatsapp_normalize_sets_channel_and_metadata():
    adapter = WhatsAppAdapter()
    payload = {"Body": "hi", "From": "+1555", "MessageSid": "abc", "Extra": "meta"}
    envelope = adapter.normalize(InboundEvent(body=payload))
    assert envelope.session.channel == "whatsapp"
    assert envelope.metadata == payload


def test_whatsapp_deduplicates_message_ids():
    adapter = WhatsAppAdapter()
    event = InboundEvent(body={"Body": "hi", "From": "+1555", "MessageSid": "abc"})
    adapter.normalize(event)
    try:
        adapter.normalize(event)
        raised = False
    except ValueError:
        raised = True
    assert raised


def test_whatsapp_normalize_alt_payload_keys():
    adapter = WhatsAppAdapter()
    event = InboundEvent(body={"text": "yo", "from": "+1777", "message_id": "xyz"})
    envelope = adapter.normalize(event)
    assert envelope.text == "yo"
    assert envelope.session.user_id == "+1777"


def test_whatsapp_normalize_allows_missing_message_id():
    adapter = WhatsAppAdapter()
    event = InboundEvent(body={"Body": "hi", "From": "+1555"})
    adapter.normalize(event)
    adapter.normalize(event)


def test_message_envelope_default_metadata_is_isolated():
    session = SessionIdentity(channel="whatsapp", user_id="+1555")
    first = MessageEnvelope(text="hi", session=session)
    second = MessageEnvelope(text="yo", session=session)
    first.metadata["x"] = "y"
    assert second.metadata == {}


@dataclass
class DummyProvider:
    sent: list[tuple[str, str]]

    def send_message(self, to_number: str, body: str) -> dict:
        self.sent.append((to_number, body))
        return {"to": to_number, "body": body, "provider": "dummy"}


def test_whatsapp_send_requires_provider():
    adapter = WhatsAppAdapter()
    message = OutboundMessage(text="hi", session=SessionIdentity(channel="whatsapp", user_id="+1555"))
    try:
        adapter.send(message)
        raised = False
    except RuntimeError:
        raised = True
    assert raised


def test_whatsapp_send_uses_provider():
    provider = DummyProvider(sent=[])
    adapter = WhatsAppAdapter(provider=provider)
    message = OutboundMessage(text="hi", session=SessionIdentity(channel="whatsapp", user_id="+1555"))
    response = adapter.send(message)
    assert provider.sent == [("+1555", "hi")]
    assert response == {"to": "+1555", "body": "hi", "provider": "dummy"}


def test_twilio_provider_includes_meta():
    provider = TwilioProvider(account_sid="sid", auth_token="token", from_number="+1555")
    response = provider.send_message(to_number="+1666", body="hello")
    assert response["provider"] == provider.meta.name
    assert response["to"] == "+1666"
    assert provider.meta.base_url == "https://api.twilio.com"


def test_webhook_server_invokes_handler():
    adapter = WhatsAppAdapter()
    server = WebhookServer(adapter=adapter)
    received: list[MessageEnvelope] = []

    def handler(envelope: MessageEnvelope) -> None:
        received.append(envelope)

    server.handle({"Body": "hi", "From": "+1555", "MessageSid": "abc"}, handler)
    assert len(received) == 1
    assert received[0].text == "hi"


def test_webhook_server_ignores_duplicate():
    adapter = WhatsAppAdapter()
    server = WebhookServer(adapter=adapter)
    received: list[MessageEnvelope] = []

    def handler(envelope: MessageEnvelope) -> None:
        received.append(envelope)

    payload = {"Body": "hi", "From": "+1555", "MessageSid": "abc"}
    server.handle(payload, handler)
    server.handle(payload, handler)
    assert len(received) == 1


def test_webhook_server_propagates_unexpected_errors():
    class BadAdapter:
        def normalize(self, event):
            raise RuntimeError("boom")

    server = WebhookServer(adapter=BadAdapter())
    try:
        server.handle({"Body": "hi"}, lambda envelope: None)
        raised = False
    except RuntimeError:
        raised = True
    assert raised


def test_transport_registry_lists_defaults():
    registry = default_transport_registry()
    assert registry.list() == ["cli", "whatsapp"]


def test_transport_registry_create_unknown_raises():
    registry = TransportRegistry()
    registry.register(TransportSpec(name="whatsapp", factory=WhatsAppAdapter))
    try:
        registry.create("missing")
        raised = False
    except KeyError:
        raised = True
    assert raised


def test_transport_registry_create_returns_instance():
    registry = TransportRegistry()
    registry.register(TransportSpec(name="cli", factory=CliTransport))
    transport = registry.create("cli")
    assert isinstance(transport, CliTransport)


def test_transport_registry_create_returns_whatsapp_instance():
    registry = TransportRegistry()
    registry.register(TransportSpec(name="whatsapp", factory=WhatsAppAdapter))
    transport = registry.create("whatsapp")
    assert isinstance(transport, WhatsAppAdapter)


def test_transport_registry_create_returns_new_instance_each_time():
    registry = TransportRegistry()
    registry.register(TransportSpec(name="cli", factory=CliTransport))
    first = registry.create("cli")
    second = registry.create("cli")
    assert first is not second


def test_transport_registry_whatsapp_returns_new_instance_each_time():
    registry = TransportRegistry()
    registry.register(TransportSpec(name="whatsapp", factory=WhatsAppAdapter))
    first = registry.create("whatsapp")
    second = registry.create("whatsapp")
    assert first is not second


def test_transport_registry_register_many_and_sorted_list():
    registry = TransportRegistry()
    registry.register_many(
        [
            TransportSpec(name="whatsapp", factory=WhatsAppAdapter),
            TransportSpec(name="cli", factory=CliTransport),
        ]
    )
    assert registry.list() == ["cli", "whatsapp"]


def test_default_transport_specs_returns_cli_and_whatsapp():
    specs = default_transport_specs()
    assert [spec.name for spec in specs] == ["cli", "whatsapp"]


def test_cli_transport_normalize_raises():
    transport = CliTransport()
    event = InboundEvent(body={"text": "hi"})
    try:
        transport.normalize(event)
        raised = False
    except NotImplementedError:
        raised = True
    assert raised


def test_cli_transport_send_raises():
    transport = CliTransport()
    message = OutboundMessage(text="hi", session=SessionIdentity(channel="cli", user_id="local"))
    try:
        transport.send(message)
        raised = False
    except NotImplementedError:
        raised = True
    assert raised
