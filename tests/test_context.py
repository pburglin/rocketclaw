from datetime import datetime

from rocketclaw.core.context_builder import ContextBuilder
from rocketclaw.core.agent_runtime import AgentRuntime
from rocketclaw.engine.model_provider import LocalEchoProvider
from rocketclaw.memory.memory_store import MemoryStore
from rocketclaw.config.settings import SETTINGS, ensure_layout
from rocketclaw.tools.tool_registry import default_registry
from rocketclaw.transports.base import MessageEnvelope, SessionIdentity


def test_context_order(tmp_path, monkeypatch):
    monkeypatch.setattr(SETTINGS, "home", tmp_path)
    ensure_layout()
    memory = MemoryStore()
    memory.write("episodic", "e1.txt", "episodic")
    builder = ContextBuilder(memory=memory)
    slices = builder.build("hello", semantic_query=None)
    names = [s.name for s in slices]
    assert names[0] == "SOUL"
    assert names[1] == "USER"
    assert names[-1] == "CONVERSATION"


def test_agent_runtime_writes_episodic(tmp_path, monkeypatch):
    monkeypatch.setattr(SETTINGS, "home", tmp_path)
    ensure_layout()
    builder = ContextBuilder(memory=MemoryStore())
    runtime = AgentRuntime(
        model=LocalEchoProvider(),
        tools=default_registry(memory_store=builder.memory),
        context_builder=builder,
    )
    envelope = MessageEnvelope(text="hello", session=SessionIdentity(channel="cli", user_id="local"))
    runtime.handle(envelope)
    entries = list(builder.memory.list_bucket("episodic"))
    assert entries
    today = datetime.now().strftime("%Y-%m-%d")
    assert any(today in path.name for path in entries)


def test_context_builder_uses_injected_searcher(tmp_path, monkeypatch):
    monkeypatch.setattr(SETTINGS, "home", tmp_path)
    ensure_layout()
    memory = MemoryStore()
    memory.write("semantic", "one.md", "match me")
    memory.write("semantic", "two.md", "skip me")

    def fake_search(paths, query: str):
        return [path for path in paths if path.name == "one.md" and query == "match"]

    builder = ContextBuilder(memory=memory, searcher=fake_search)
    slices = builder.build("hello", semantic_query="match")
    semantic = [s for s in slices if s.name == "SEMANTIC"]
    assert semantic
    assert "match me" in semantic[0].content
