import base64
import uuid

import pytest

from backend.app.service import AdventureService


class InMemorySessionRepository:
    def __init__(self):
        self.sessions = {}

    def get_or_create(self, session_id: str):
        if session_id in self.sessions:
            return self.sessions[session_id], False
        row = {
            "session_id": session_id,
            "save_data": "",
            "created_at": "2026-01-01T00:00:00",
            "updated_at": "2026-01-01T00:00:00",
        }
        self.sessions[session_id] = row
        return row, True

    def set_save_data(self, session_id: str, save_data: str):
        row, _ = self.get_or_create(session_id)
        row["save_data"] = save_data
        row["updated_at"] = "2026-01-01T00:00:01"
        return row


class FakeAdventure:
    def __init__(self):
        self.loaded = b""

    def get_intro(self):
        return "Welcome to the game"

    def execute(self, tokens):
        return f"**Echo** {' '.join(tokens)}"

    def admin_save(self):
        return b"next-save"

    def admin_load(self, input_bytes):
        self.loaded = input_bytes


def test_create_session_generates_uuid_when_missing():
    repo = InMemorySessionRepository()
    service = AdventureService(
        repository=repo,
        adventure_factory=FakeAdventure,
        markdown_renderer=lambda text: text,
    )

    result = service.create_session(None)

    parsed = uuid.UUID(result["session_id"])
    assert str(parsed) == result["session_id"]
    assert result["created"] is True
    assert result["intro_html"] == "Welcome to the game"


def test_create_session_with_existing_id_is_idempotent():
    repo = InMemorySessionRepository()
    service = AdventureService(
        repository=repo,
        adventure_factory=FakeAdventure,
        markdown_renderer=lambda text: text,
    )

    first = service.create_session("fixed-id")
    second = service.create_session("fixed-id")

    assert first["session_id"] == "fixed-id"
    assert first["created"] is True
    assert first["intro_html"] == "Welcome to the game"
    assert second == {"session_id": "fixed-id", "created": False}


def test_execute_command_loads_and_saves_state():
    repo = InMemorySessionRepository()
    session_id = "session-1"
    repo.set_save_data(session_id, base64.b64encode(b"prior-save").decode("ascii"))
    adventure = FakeAdventure()
    service = AdventureService(
        repository=repo,
        adventure_factory=lambda: adventure,
        markdown_renderer=lambda text: f"<p>{text}</p>",
    )

    result = service.execute_command(session_id=session_id, command="look around")

    assert adventure.loaded == b"prior-save"
    assert result["output_html"] == "<p>**Echo** look around</p>"
    assert repo.sessions[session_id]["save_data"] == base64.b64encode(b"next-save").decode("ascii")


def test_execute_command_rejects_empty_input():
    repo = InMemorySessionRepository()
    service = AdventureService(
        repository=repo,
        adventure_factory=FakeAdventure,
        markdown_renderer=lambda text: text,
    )

    with pytest.raises(ValueError, match="Command must not be empty"):
        service.execute_command(session_id="session-1", command="   ")


def test_reset_session_clears_saved_data():
    repo = InMemorySessionRepository()
    session_id = "session-reset"
    repo.set_save_data(session_id, base64.b64encode(b"old").decode("ascii"))
    service = AdventureService(
        repository=repo,
        adventure_factory=FakeAdventure,
        markdown_renderer=lambda text: text,
    )

    result = service.reset_session(session_id)

    assert result["reset"] is True
    assert repo.sessions[session_id]["save_data"] == ""
