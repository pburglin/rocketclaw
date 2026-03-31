from rocketclaw.config.settings import SETTINGS
from rocketclaw.skills.inventory import add_skill, list_skills


def test_skills_inventory(tmp_path, monkeypatch):
    monkeypatch.setattr(SETTINGS, "home", tmp_path)
    add_skill("new-skill")
    skills = list_skills()
    assert "new-skill" in skills
