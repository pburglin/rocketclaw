from pathlib import Path

from rocketclaw.memory.retrieval import simple_search


def test_simple_search_matches_and_skips_unreadable(tmp_path):
    first = tmp_path / "one.txt"
    second = tmp_path / "two.txt"
    directory = tmp_path / "folder"
    first.write_text("Hello world")
    second.write_text("Nothing to see here")
    directory.mkdir()

    matches = simple_search([first, second, directory], "world")
    assert matches == [first]


def test_simple_search_is_case_insensitive(tmp_path):
    target = tmp_path / "note.txt"
    target.write_text("MixedCase Entry")

    matches = simple_search([target], "mixedcase")
    assert matches == [target]
