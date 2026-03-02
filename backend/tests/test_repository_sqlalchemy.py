from pathlib import Path

from backend.app.db import create_session_factory, initialize_database
from backend.app.repository import PostgresSessionRepository


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
