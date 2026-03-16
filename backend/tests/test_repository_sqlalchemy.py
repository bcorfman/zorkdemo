from pathlib import Path

from backend.app.db import create_session_factory, initialize_database
from backend.app.repository import PostgresSaveSlotRepository, PostgresSessionRepository


def test_get_or_create_is_idempotent(tmp_path: Path):
    db_path = tmp_path / "sessions.db"
    database_url = f"sqlite+pysqlite:///{db_path}"
    initialize_database(database_url)
    session_factory = create_session_factory(database_url)
    repository = PostgresSessionRepository(session_factory)

    row1, created1 = repository.get_or_create("abc123")
    row2, created2 = repository.get_or_create("abc123")

    assert created1 is True
    assert created2 is False
    assert row1["session_id"] == "abc123"
    assert row2["session_id"] == "abc123"
    assert row2["save_data"] == ""
    assert row2["pending_action"] is None
    assert row2["pending_slot_name"] is None


def test_set_save_data_persists_and_updates(tmp_path: Path):
    db_path = tmp_path / "sessions.db"
    database_url = f"sqlite+pysqlite:///{db_path}"
    initialize_database(database_url)
    session_factory = create_session_factory(database_url)
    repository = PostgresSessionRepository(session_factory)

    first, _ = repository.get_or_create("session-1")
    updated = repository.set_save_data("session-1", "new-save-payload")

    assert updated["session_id"] == "session-1"
    assert updated["save_data"] == "new-save-payload"
    assert updated["updated_at"] >= first["updated_at"]


def test_set_save_data_creates_if_missing(tmp_path: Path):
    db_path = tmp_path / "sessions.db"
    database_url = f"sqlite+pysqlite:///{db_path}"
    initialize_database(database_url)
    session_factory = create_session_factory(database_url)
    repository = PostgresSessionRepository(session_factory)

    updated = repository.set_save_data("session-2", "initial")

    assert updated["session_id"] == "session-2"
    assert updated["save_data"] == "initial"


def test_pending_confirmation_round_trip(tmp_path: Path):
    db_path = tmp_path / "sessions.db"
    database_url = f"sqlite+pysqlite:///{db_path}"
    initialize_database(database_url)
    session_factory = create_session_factory(database_url)
    repository = PostgresSessionRepository(session_factory)

    pending = repository.set_pending_confirmation("session-3", "restore_slot", "slotA")
    assert pending["pending_action"] == "restore_slot"
    assert pending["pending_slot_name"] == "slotA"

    cleared = repository.clear_pending_confirmation("session-3")
    assert cleared["pending_action"] is None
    assert cleared["pending_slot_name"] is None


def test_save_slot_repository_scoped_crud(tmp_path: Path):
    db_path = tmp_path / "sessions.db"
    database_url = f"sqlite+pysqlite:///{db_path}"
    initialize_database(database_url)
    session_factory = create_session_factory(database_url)
    repository = PostgresSaveSlotRepository(session_factory)

    repository.upsert_slot("session-A", "slot1", "save-1")
    repository.upsert_slot("session-A", "slot2", "save-2")
    repository.upsert_slot("session-B", "slot1", "save-other")

    assert repository.has_slot("session-A", "slot1") is True
    assert repository.has_slot("session-A", "missing") is False
    assert repository.get_slot("session-A", "slot1")["save_data"] == "save-1"
    assert [row["slot_name"] for row in repository.list_slots("session-A")] == ["slot1", "slot2"]

    deleted = repository.delete_all_slots("session-A")
    assert deleted == 2
    assert repository.list_slots("session-A") == []
    assert repository.has_slot("session-B", "slot1") is True
