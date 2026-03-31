from rocketclaw.config.settings import SETTINGS
from rocketclaw.tools.tool_registry import (
    Tool,
    ToolRegistry,
    build_default_tools,
    create_filesystem_tool,
    create_http_fetch_tool,
    create_shell_command_tool,
    default_registry,
)


def test_tool_registry_register_and_execute():
    registry = ToolRegistry()
    tool = Tool(
        name="echo",
        schema={"type": "object"},
        permissions=["read"],
        handler=lambda payload: payload.get("value"),
    )
    registry.register(tool)
    assert registry.list() == ["echo"]
    assert registry.execute("echo", {"value": "hi"}) == "hi"


def test_filesystem_tool_factory_echoes_path():
    tool = create_filesystem_tool()
    assert tool.name == "filesystem"
    assert tool.permissions == ["read"]
    assert tool.handler({"path": "/tmp/notes.txt"}) == "/tmp/notes.txt"


def test_tool_registry_unknown_tool_raises():
    registry = ToolRegistry()
    try:
        registry.execute("missing", {})
        raised = False
    except KeyError:
        raised = True
    assert raised


def test_default_registry_includes_filesystem():
    registry = default_registry()
    assert "filesystem" in registry.list()
    assert "memory_write" in registry.list()
    assert "memory_search" in registry.list()
    assert "http_fetch" in registry.list()
    assert "shell_command" in registry.list()
    assert "task_manager" in registry.list()


def test_filesystem_tool_echoes_path():
    registry = default_registry()
    response = registry.execute("filesystem", {"path": "/tmp/notes.txt"})
    assert response == "/tmp/notes.txt"


def test_task_manager_tool_records_task(tmp_path, monkeypatch):
    monkeypatch.setattr(SETTINGS, "home", tmp_path)
    registry = default_registry()
    response = registry.execute("task_manager", {"action": "add", "task": "follow up"})
    assert response == "task recorded: follow up (task-0001)"


def test_memory_tools_execute(tmp_path, monkeypatch):
    monkeypatch.setattr(SETTINGS, "home", tmp_path)
    registry = default_registry()
    registry.execute(
        "memory_write",
        {"bucket": "semantic", "name": "note.md", "content": "hello world"},
    )
    matches = registry.execute("memory_search", {"bucket": "semantic", "query": "hello"})
    assert any("hello world" in match for match in matches)


def test_shell_command_disabled(monkeypatch):
    monkeypatch.delenv("ROCKETCLAW_ALLOW_SHELL", raising=False)
    registry = default_registry()
    response = registry.execute("shell_command", {"command": "echo hi"})
    assert response == "shell execution disabled"


def test_shell_command_enabled(monkeypatch):
    monkeypatch.setenv("ROCKETCLAW_ALLOW_SHELL", "1")
    registry = default_registry()
    response = registry.execute("shell_command", {"command": "echo hi"})
    assert response == "hi"


def test_http_fetch_uses_httpx(monkeypatch):
    class DummyResponse:
        def __init__(self, text: str) -> None:
            self.text = text

    def fake_get(url: str, timeout: float):
        return DummyResponse(text=f"ok:{url}:{timeout}")

    monkeypatch.setattr("rocketclaw.tools.tool_registry.httpx.get", fake_get)
    registry = default_registry()
    response = registry.execute("http_fetch", {"url": "https://example.com"})
    assert response == "ok:https://example.com:10"


def test_http_fetch_tool_factory_uses_injected_client():
    class DummyResponse:
        def __init__(self, text: str) -> None:
            self.text = text

    def fake_get(url: str, timeout: float):
        return DummyResponse(text=f"factory:{url}:{timeout}")

    tool = create_http_fetch_tool(fake_get)
    assert tool.handler({"url": "https://example.com"}) == "factory:https://example.com:10"


def test_default_registry_allows_http_injection():
    class DummyResponse:
        def __init__(self, text: str) -> None:
            self.text = text

    def fake_get(url: str, timeout: float):
        return DummyResponse(text=f"injected:{url}:{timeout}")

    registry = default_registry(http_get=fake_get)
    response = registry.execute("http_fetch", {"url": "https://example.com"})
    assert response == "injected:https://example.com:10"


def test_default_registry_allows_memory_searcher_injection(tmp_path):
    class DummyMemory:
        def __init__(self) -> None:
            self.base = tmp_path

        def list_bucket(self, bucket: str):
            path = tmp_path / bucket
            path.mkdir(parents=True, exist_ok=True)
            (path / "note.md").write_text("hello")
            (path / "skip.md").write_text("ignore")
            return list(path.glob("*.md"))

    def fake_search(paths, query: str):
        return [path for path in paths if path.name == "note.md" and query == "hello"]

    registry = default_registry(memory_store=DummyMemory(), memory_searcher=fake_search)
    matches = registry.execute("memory_search", {"bucket": "semantic", "query": "hello"})
    assert matches == ["hello"]


def test_memory_write_returns_path_string(tmp_path, monkeypatch):
    monkeypatch.setattr(SETTINGS, "home", tmp_path)
    registry = default_registry()
    response = registry.execute(
        "memory_write",
        {"bucket": "semantic", "name": "note.md", "content": "hello"},
    )
    assert response.endswith("semantic/note.md")


def test_default_registry_allows_shell_runner_injection():
    def fake_shell(command: str) -> str:
        return f"ran:{command}"

    registry = default_registry(shell_runner=fake_shell)
    response = registry.execute("shell_command", {"command": "echo hi"})
    assert response == "ran:echo hi"


def test_shell_command_tool_factory_uses_runner():
    def fake_shell(command: str) -> str:
        return f"factory:{command}"

    tool = create_shell_command_tool(fake_shell)
    assert tool.handler({"command": "echo hi"}) == "factory:echo hi"


def test_default_registry_uses_injected_memory_store(tmp_path):
    class DummyMemory:
        def __init__(self) -> None:
            self.writes: list[tuple[str, str, str]] = []

        def write(self, bucket: str, name: str, content: str):
            self.writes.append((bucket, name, content))
            path = tmp_path / bucket / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            return path

        def list_bucket(self, bucket: str):
            target = tmp_path / bucket
            if not target.exists():
                return []
            return list(target.glob("*.md"))

    memory = DummyMemory()
    registry = default_registry(memory_store=memory)
    registry.execute(
        "memory_write",
        {"bucket": "semantic", "name": "note.md", "content": "hello"},
    )
    matches = registry.execute("memory_search", {"bucket": "semantic", "query": "hello"})
    assert memory.writes == [("semantic", "note.md", "hello")]
    assert any("hello" in match for match in matches)


def test_tool_registry_register_many_and_sorted_list():
    registry = ToolRegistry()
    registry.register_many(
        [
            Tool(name="zulu", schema={"type": "object"}, permissions=["read"], handler=lambda payload: "z"),
            Tool(name="alpha", schema={"type": "object"}, permissions=["read"], handler=lambda payload: "a"),
        ]
    )
    assert registry.list() == ["alpha", "zulu"]


def test_build_default_tools_returns_expected_names(tmp_path):
    class DummyMemory:
        def write(self, bucket: str, name: str, content: str):
            path = tmp_path / bucket / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            return path

        def list_bucket(self, bucket: str):
            return list((tmp_path / bucket).glob("*.md")) if (tmp_path / bucket).exists() else []

    tools = build_default_tools(
        memory_store=DummyMemory(),
        memory_searcher=lambda paths, query: [],
        http_get=lambda url, timeout: type("Response", (), {"text": "ok"})(),
        shell_runner=lambda command: command,
    )
    assert [tool.name for tool in tools] == [
        "filesystem",
        "memory_write",
        "memory_search",
        "http_fetch",
        "shell_command",
        "task_manager",
    ]
