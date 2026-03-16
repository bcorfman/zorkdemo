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
            "pending_action": None,
            "pending_slot_name": None,
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

    def set_pending_confirmation(self, session_id: str, action: str, slot_name: str | None):
        row, _ = self.get_or_create(session_id)
        row["pending_action"] = action
        row["pending_slot_name"] = slot_name
        row["updated_at"] = "2026-01-01T00:00:01"
        return row

    def clear_pending_confirmation(self, session_id: str):
        row, _ = self.get_or_create(session_id)
        row["pending_action"] = None
        row["pending_slot_name"] = None
        row["updated_at"] = "2026-01-01T00:00:01"
        return row


class InMemorySaveSlotRepository:
    def __init__(self):
        self.slots: dict[tuple[str, str], dict[str, str]] = {}

    def has_slot(self, session_id: str, slot_name: str) -> bool:
        return (session_id, slot_name) in self.slots

    def upsert_slot(self, session_id: str, slot_name: str, save_data: str):
        key = (session_id, slot_name)
        self.slots[key] = {
            "session_id": session_id,
            "slot_name": slot_name,
            "save_data": save_data,
            "created_at": "2026-01-01T00:00:00",
            "updated_at": "2026-01-01T00:00:01",
        }
        return self.slots[key]

    def get_slot(self, session_id: str, slot_name: str):
        return self.slots.get((session_id, slot_name))

    def list_slots(self, session_id: str):
        rows = [row for row in self.slots.values() if row["session_id"] == session_id]
        return sorted(rows, key=lambda row: row["slot_name"])

    def delete_all_slots(self, session_id: str) -> int:
        keys = [key for key in self.slots if key[0] == session_id]
        for key in keys:
            del self.slots[key]
        return len(keys)


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


class FakeAdventureWithDuplicateIntro(FakeAdventure):
    def get_intro(self):
        return (
            "ZORK I: The Great Underground Empire\n\n"
            "West of House\n"
            "You are standing in an open field west of a white house, with a boarded front door.\n"
            "There is a small mailbox here.\n\n"
            "West of House\n"
            "You are standing in an open field west of a white house, with a boarded front door.\n"
            "There is a small mailbox here."
        )


def _build_service(repository=None, slots=None):
    return AdventureService(
        repository=repository or InMemorySessionRepository(),
        save_slot_repository=slots or InMemorySaveSlotRepository(),
        adventure_factory=FakeAdventure,
        markdown_renderer=lambda text: text,
    )


def test_create_session_generates_uuid_when_missing():
    service = _build_service()

    result = service.create_session(None)

    parsed = uuid.UUID(result["session_id"])
    assert str(parsed) == result["session_id"]
    assert result["created"] is True
    assert result["intro_html"] == "Welcome to the game"


def test_create_session_with_existing_id_is_idempotent():
    service = _build_service()

    first = service.create_session("fixed-id")
    second = service.create_session("fixed-id")

    assert first["session_id"] == "fixed-id"
    assert first["created"] is True
    assert first["intro_html"] == "Welcome to the game"
    assert second == {"session_id": "fixed-id", "created": False}


def test_execute_command_loads_and_saves_state():
    repository = InMemorySessionRepository()
    session_id = "session-1"
    repository.set_save_data(session_id, base64.b64encode(b"prior-save").decode("ascii"))
    adventure = FakeAdventure()
    service = AdventureService(
        repository=repository,
        save_slot_repository=InMemorySaveSlotRepository(),
        adventure_factory=lambda: adventure,
        markdown_renderer=lambda text: f"<p>{text}</p>",
    )

    result = service.execute_command(session_id=session_id, command="look around")

    assert adventure.loaded == b"prior-save"
    assert result["output_html"] == "<p>**Echo** look around</p>"
    assert repository.sessions[session_id]["save_data"] == base64.b64encode(b"next-save").decode("ascii")


def test_execute_command_rejects_empty_input():
    service = _build_service()

    with pytest.raises(ValueError, match="Command must not be empty"):
        service.execute_command(session_id="session-1", command="   ")


def test_reset_session_reseeds_state_and_returns_intro():
    repository = InMemorySessionRepository()
    session_id = "session-reset"
    repository.set_save_data(session_id, base64.b64encode(b"old").decode("ascii"))
    service = AdventureService(
        repository=repository,
        save_slot_repository=InMemorySaveSlotRepository(),
        adventure_factory=FakeAdventure,
        markdown_renderer=lambda text: text,
    )

    result = service.reset_session(session_id)

    assert result["reset"] is True
    assert result["intro_html"] == "Welcome to the game"
    assert repository.sessions[session_id]["save_data"] == base64.b64encode(b"next-save").decode("ascii")


def test_create_session_collapses_duplicate_intro_room_block():
    service = AdventureService(
        repository=InMemorySessionRepository(),
        save_slot_repository=InMemorySaveSlotRepository(),
        adventure_factory=FakeAdventureWithDuplicateIntro,
        markdown_renderer=lambda text: text,
    )

    result = service.create_session("fixed-id")

    assert result["created"] is True
    assert result["intro_html"].count("West of House") == 1
    assert ">" not in result["intro_html"]


def test_execute_command_strips_prompt_markers():
    class PromptAdventure(FakeAdventure):
        def execute(self, tokens):
            return "> West of House\nThere is a small mailbox here.\n\n>"

    service = AdventureService(
        repository=InMemorySessionRepository(),
        save_slot_repository=InMemorySaveSlotRepository(),
        adventure_factory=PromptAdventure,
        markdown_renderer=lambda text: text,
    )

    result = service.execute_command(session_id="session-1", command="look")

    assert result["output_html"] == "West of House\nThere is a small mailbox here."


def test_save_and_restore_commands_with_confirmations():
    repository = InMemorySessionRepository()
    slots = InMemorySaveSlotRepository()
    service = AdventureService(
        repository=repository,
        save_slot_repository=slots,
        adventure_factory=FakeAdventure,
        markdown_renderer=lambda text: text,
    )
    session_id = "session-cmd"
    service.create_session(session_id)

    save_new = service.execute_command(session_id, "save SLOT1")
    assert save_new["output_html"] == "SLOT1 saved."

    save_existing = service.execute_command(session_id, "save SLOT1")
    assert save_existing["output_html"] == "SLOT1 already exists. Do you wish to overwrite it (Y/N)?"
    assert repository.sessions[session_id]["pending_action"] == "save_overwrite"
    assert repository.sessions[session_id]["pending_slot_name"] == "SLOT1"

    blocked = service.execute_command(session_id, "look")
    assert blocked["output_html"] == "Please answer Y or N."

    cancelled = service.execute_command(session_id, "n")
    assert cancelled["output_html"] == "Overwrite cancelled."
    assert repository.sessions[session_id]["pending_action"] is None

    restore_prompt = service.execute_command(session_id, "restore SLOT1")
    assert restore_prompt["output_html"] == "Do you wish to restore over the game in progress (Y/N)?"

    restored = service.execute_command(session_id, "Y")
    assert restored["output_html"] == "SLOT1 restored."
    assert repository.sessions[session_id]["pending_action"] is None


def test_bare_save_and_restore_list_slots():
    repository = InMemorySessionRepository()
    slots = InMemorySaveSlotRepository()
    service = AdventureService(
        repository=repository,
        save_slot_repository=slots,
        adventure_factory=FakeAdventure,
        markdown_renderer=lambda text: text,
    )
    session_id = "session-list"
    service.create_session(session_id)

    empty_list = service.execute_command(session_id, "save")
    assert empty_list["output_html"] == "No saved slots yet."

    service.execute_command(session_id, "save SLOT2")
    service.execute_command(session_id, "save SLOT1")

    listed = service.execute_command(session_id, "restore")
    assert listed["output_html"] == "Saved slots:\n- SLOT1\n- SLOT2"


def test_reset_slots_requires_confirmation_and_is_scoped_to_session():
    repository = InMemorySessionRepository()
    slots = InMemorySaveSlotRepository()
    service = AdventureService(
        repository=repository,
        save_slot_repository=slots,
        adventure_factory=FakeAdventure,
        markdown_renderer=lambda text: text,
    )
    service.create_session("session-a")
    service.create_session("session-b")
    service.execute_command("session-a", "save A1")
    service.execute_command("session-a", "save A2")
    service.execute_command("session-b", "save B1")

    prompt = service.execute_command("session-a", "reset slots")
    assert prompt["output_html"] == "Do you wish to delete all saved slots for this session (Y/N)?"
    assert slots.has_slot("session-a", "A1") is True

    cancelled = service.execute_command("session-a", "N")
    assert cancelled["output_html"] == "Reset slots cancelled."
    assert slots.has_slot("session-a", "A1") is True

    service.execute_command("session-a", "reset slots")
    confirmed = service.execute_command("session-a", "y")
    assert confirmed["output_html"] == "All saved slots deleted for this session."
    assert slots.list_slots("session-a") == []
    assert slots.has_slot("session-b", "B1") is True


def test_slots_can_be_restored_across_new_sessions_for_same_player():
    repository = InMemorySessionRepository()
    slots = InMemorySaveSlotRepository()
    service = AdventureService(
        repository=repository,
        save_slot_repository=slots,
        adventure_factory=FakeAdventure,
        markdown_renderer=lambda text: text,
    )
    player_id = "player-abc"
    first_session = "session-1"
    second_session = "session-2"

    service.create_session(first_session)
    saved = service.execute_command(first_session, "save SLOT1", player_id=player_id)
    assert saved["output_html"] == "SLOT1 saved."

    service.create_session(second_session)
    list_from_new_session = service.execute_command(second_session, "restore", player_id=player_id)
    assert "SLOT1" in list_from_new_session["output_html"]

    prompt = service.execute_command(second_session, "restore SLOT1", player_id=player_id)
    assert prompt["output_html"] == "Do you wish to restore over the game in progress (Y/N)?"
    restored = service.execute_command(second_session, "Y", player_id=player_id)
    assert restored["output_html"] == "SLOT1 restored."
