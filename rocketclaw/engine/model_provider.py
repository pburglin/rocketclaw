from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Iterable

import httpx

from rocketclaw.config.settings import PROVIDERS_FILE, SETTINGS


class ModelProvider:
    name: str

    def complete(self, prompt: str) -> str:
        raise NotImplementedError


@dataclass
class LocalEchoProvider(ModelProvider):
    name: str = "local-echo"

    def complete(self, prompt: str) -> str:
        return f"[Rocket] {prompt[:1200]}"


@dataclass
class PlaceholderProvider(ModelProvider):
    name: str

    def complete(self, prompt: str) -> str:
        raise RuntimeError(f"Model provider not configured: {self.name}")


@dataclass
class OpenAICompatibleProvider(ModelProvider):
    name: str
    base_url: str
    model: str
    api_key_env: str
    timeout_seconds: int = 30

    def complete(self, prompt: str) -> str:
        api_key = os.getenv(self.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing API key env: {self.api_key_env}")
        url = self.base_url.rstrip("/") + "/chat/completions"
        response = httpx.post(
            url,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": self.model, "messages": [{"role": "user", "content": prompt}]},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        choices = payload.get("choices", [])
        if not choices:
            raise RuntimeError("No choices returned from provider")
        message = choices[0].get("message") or {}
        content = message.get("content")
        if content:
            return str(content)
        text = choices[0].get("text")
        if text:
            return str(text)
        raise RuntimeError("No content returned from provider")


@dataclass
class RoutingModelProvider(ModelProvider):
    providers: list[ModelProvider]
    cooldown_seconds: int = 60
    provider_cooldowns: dict[str, int] | None = None
    name: str = "routing"
    _cooldowns: dict[str, float] = None

    def __post_init__(self) -> None:
        if self._cooldowns is None:
            self._cooldowns = {}
        if self.provider_cooldowns is None:
            self.provider_cooldowns = {}

    def complete(self, prompt: str) -> str:
        last_error: Exception | None = None
        for provider in self._available_providers():
            try:
                return provider.complete(prompt)
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                cooldown = self.provider_cooldowns.get(provider.name, self.cooldown_seconds)
                self._cooldowns[provider.name] = time.time() + cooldown
        raise RuntimeError("All providers failed") from last_error

    def _available_providers(self) -> Iterable[ModelProvider]:
        now = time.time()
        for provider in self.providers:
            cooldown_until = self._cooldowns.get(provider.name, 0)
            if cooldown_until <= now:
                yield provider


def _provider_from_name(name: str) -> ModelProvider:
    if name == "local-echo":
        return LocalEchoProvider()
    return PlaceholderProvider(name=name)


def _provider_from_config(raw: dict[str, object]) -> ModelProvider:
    provider_type = str(raw.get("type", "local-echo"))
    name = str(raw.get("name", provider_type))
    if provider_type == "local-echo":
        return LocalEchoProvider(name=name)
    if provider_type == "openai_compatible":
        base_url = str(raw.get("base_url", "https://api.openai.com/v1"))
        model = str(raw.get("model", "gpt-4o-mini"))
        api_key_env = str(raw.get("api_key_env", "OPENAI_API_KEY"))
        timeout_seconds = int(raw.get("timeout_seconds", 30))
        return OpenAICompatibleProvider(
            name=name,
            base_url=base_url,
            model=model,
            api_key_env=api_key_env,
            timeout_seconds=timeout_seconds,
        )
    return PlaceholderProvider(name=name)


def from_config() -> ModelProvider:
    providers_path = SETTINGS.config_dir / PROVIDERS_FILE
    if providers_path.exists():
        raw = json.loads(providers_path.read_text())
        providers_raw = raw.get("providers", [])
        cooldown_default = int(raw.get("cooldown_seconds", 60))
        if isinstance(providers_raw, list) and providers_raw:
            providers: list[ModelProvider] = []
            cooldowns: dict[str, int] = {}
            for item in providers_raw:
                if not isinstance(item, dict):
                    continue
                provider = _provider_from_config(item)
                providers.append(provider)
                if "cooldown_seconds" in item:
                    cooldowns[provider.name] = int(item["cooldown_seconds"])
            if providers:
                return RoutingModelProvider(
                    providers=providers,
                    cooldown_seconds=cooldown_default,
                    provider_cooldowns=cooldowns,
                )

    return from_env()


def from_env() -> ModelProvider:
    providers_raw = os.getenv("ROCKETCLAW_MODEL_PROVIDERS")
    cooldown_raw = os.getenv("ROCKETCLAW_MODEL_COOLDOWN_SECONDS")
    if providers_raw:
        try:
            names = json.loads(providers_raw)
            if isinstance(names, list) and names:
                providers = [_provider_from_name(str(name)) for name in names]
                cooldown = int(cooldown_raw) if cooldown_raw else 60
                return RoutingModelProvider(providers=providers, cooldown_seconds=cooldown)
        except json.JSONDecodeError:
            pass

    name = os.getenv("ROCKETCLAW_MODEL", "local-echo")
    return _provider_from_name(name)
