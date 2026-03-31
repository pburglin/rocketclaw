from rocketclaw.transports.whatsapp.webhook_server import WebhookServer
from rocketclaw.transports.whatsapp.adapter import WhatsAppAdapter


def test_webhook_parsing():
    adapter = WhatsAppAdapter()
    server = WebhookServer(adapter=adapter)
    seen = []

    def on_message(envelope):
        seen.append(envelope.text)

    server.handle({"Body": "ping", "MessageSid": "1"}, on_message)
    assert seen == ["ping"]
