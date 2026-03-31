from rocketclaw.engine.model_provider import LocalEchoProvider, RoutingModelProvider, _provider_from_config


class FailingProvider:
    name = "failing"

    def complete(self, prompt: str) -> str:  # pragma: no cover - simple stub
        raise RuntimeError("boom")


def test_routing_provider_fallback():
    routing = RoutingModelProvider(providers=[FailingProvider(), LocalEchoProvider()])
    result = routing.complete("hello")
    assert result.startswith("[Rocket]")


def test_routing_provider_all_fail():
    routing = RoutingModelProvider(providers=[FailingProvider()])
    try:
        routing.complete("hello")
    except RuntimeError as exc:
        assert "All providers failed" in str(exc)
    else:
        raise AssertionError("Expected failure")


def test_provider_from_config_openai():
    provider = _provider_from_config(
        {
            "type": "openai_compatible",
            "name": "openai",
            "base_url": "https://api.example.com/v1",
            "model": "gpt-test",
            "api_key_env": "OPENAI_API_KEY",
            "timeout_seconds": 10,
        }
    )
    assert provider.name == "openai"
    assert provider.model == "gpt-test"
