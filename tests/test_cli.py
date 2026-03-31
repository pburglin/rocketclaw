from typer.testing import CliRunner

from rocketclaw.config.settings import SETTINGS
from rocketclaw.interface.cli import app

runner = CliRunner()


def test_cli_tool_list(tmp_path, monkeypatch):
    monkeypatch.setattr(SETTINGS, "home", tmp_path)
    result = runner.invoke(app, ["tool", "list"])
    assert result.exit_code == 0


def test_cli_transport_list(tmp_path, monkeypatch):
    monkeypatch.setattr(SETTINGS, "home", tmp_path)
    result = runner.invoke(app, ["transport", "list"])
    assert result.exit_code == 0
