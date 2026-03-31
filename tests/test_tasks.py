import json

from typer.testing import CliRunner

from rocketclaw.config.settings import SETTINGS, ensure_layout
from rocketclaw.interface.cli import app
from rocketclaw.memory.memory_store import MemoryStore
from rocketclaw.memory.task_store import TaskStore
from rocketclaw.tools.tool_registry import default_registry

runner = CliRunner()


def test_task_store_create_list_complete(tmp_path, monkeypatch):
    monkeypatch.setattr(SETTINGS, "home", tmp_path)
    ensure_layout()
    store = TaskStore(memory=MemoryStore())

    first = store.create("follow up")
    second = store.create("ship feature")

    assert [record.task_id for record in store.list()] == ["task-0001", "task-0002"]
    assert first.status == "open"

    completed = store.complete("2")
    assert completed.task_id == second.task_id
    assert completed.status == "done"
    assert [record.task_id for record in store.list(status="done")] == ["task-0002"]


def test_task_manager_tool_persists_tasks(tmp_path, monkeypatch):
    monkeypatch.setattr(SETTINGS, "home", tmp_path)
    ensure_layout()
    registry = default_registry()

    added = registry.execute("task_manager", {"action": "add", "task": "follow up"})
    tasks = registry.execute("task_manager", {"action": "list"})
    completed = registry.execute("task_manager", {"action": "complete", "task_id": "task-0001"})
    done = registry.execute("task_manager", {"action": "list", "status": "done"})

    assert "task-0001" in added
    assert tasks[0]["title"] == "follow up"
    assert completed.endswith("(task-0001)")
    assert done == [tasks[0] | {"status": "done", "completed_at": done[0]["completed_at"]}]


def test_cli_task_commands(tmp_path, monkeypatch):
    monkeypatch.setattr(SETTINGS, "home", tmp_path)

    add_result = runner.invoke(app, ["task", "add", "follow up"])
    assert add_result.exit_code == 0
    assert "task-0001" in add_result.output

    list_result = runner.invoke(app, ["task", "list"])
    assert list_result.exit_code == 0
    tasks = json.loads(list_result.output)
    assert tasks[0]["title"] == "follow up"

    complete_result = runner.invoke(app, ["task", "complete", "1"])
    assert complete_result.exit_code == 0
    assert "task-0001" in complete_result.output

    done_result = runner.invoke(app, ["task", "list", "--status", "done"])
    assert done_result.exit_code == 0
    done_tasks = json.loads(done_result.output)
    assert done_tasks[0]["status"] == "done"
