from __future__ import annotations

from dataclasses import dataclass, field

from rocketclaw.transports.whatsapp.provider_meta import ProviderMeta


@dataclass
class TwilioProvider:
    account_sid: str
    auth_token: str
    from_number: str

    meta: ProviderMeta = field(
        default_factory=lambda: ProviderMeta(name="twilio", base_url="https://api.twilio.com")
    )

    def send_message(self, to_number: str, body: str) -> dict:
        # Placeholder: integrate Twilio REST API.
        return {"to": to_number, "body": body, "provider": self.meta.name}
