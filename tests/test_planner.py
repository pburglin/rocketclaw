from rocketclaw.core.planner import Planner


def test_planner_splits_on_and_then():
    planner = Planner()
    plan = planner.plan("draft report and review then send")
    assert plan.steps == ["draft report", "review", "send"]


def test_planner_splits_on_commas():
    planner = Planner()
    plan = planner.plan("one, two, three")
    assert plan.steps == ["one", "two", "three"]
