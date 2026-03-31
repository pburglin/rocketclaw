from rocketclaw.config.settings import SETTINGS
from rocketclaw.workspace.manager import (
    get_active_workspace,
    list_workspaces,
    set_active_workspace,
)


def test_workspace_switching(tmp_path, monkeypatch):
    monkeypatch.setattr(SETTINGS, "home", tmp_path)
    set_active_workspace("alpha")
    assert get_active_workspace() == "alpha"
    set_active_workspace("beta")
    assert get_active_workspace() == "beta"
    assert "alpha" in list_workspaces()
    assert "beta" in list_workspaces()
