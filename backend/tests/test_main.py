from pathlib import Path

import pytest

from backend.app.main import _DEFAULT_STORY_PATH, _resolve_story_path


class StubSettings:
    def __init__(self, story_file: str) -> None:
        self.story_file = story_file


def test_resolve_story_path_uses_configured_story_when_present(tmp_path: Path):
    custom_story = tmp_path / "custom.z3"
    custom_story.write_bytes(b"story")

    resolved = _resolve_story_path(StubSettings(story_file=str(custom_story)))

    assert resolved == custom_story


def test_resolve_story_path_falls_back_to_default_when_configured_story_missing():
    resolved = _resolve_story_path(StubSettings(story_file="/tmp/does-not-exist.z3"))

    assert resolved == _DEFAULT_STORY_PATH


def test_resolve_story_path_raises_when_no_story_exists(monkeypatch, tmp_path: Path):
    missing_default = tmp_path / "missing.z3"
    monkeypatch.setattr("backend.app.main._DEFAULT_STORY_PATH", missing_default)

    with pytest.raises(FileNotFoundError):
        _resolve_story_path(StubSettings(story_file=""))
