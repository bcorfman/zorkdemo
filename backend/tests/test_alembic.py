from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text


def test_alembic_upgrade_creates_sessions_table(tmp_path: Path):
    db_path = tmp_path / "alembic.db"
    database_url = f"sqlite+pysqlite:///{db_path}"

    config = Config("backend/alembic.ini")
    config.set_main_option("sqlalchemy.url", database_url)

    command.upgrade(config, "head")

    engine = create_engine(database_url)
    with engine.connect() as connection:
        row = connection.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='adventure_sessions'")
        ).fetchone()
        slots_row = connection.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='adventure_save_slots'")
        ).fetchone()
        session_columns = {
            column_row[1] for column_row in connection.execute(text("PRAGMA table_info(adventure_sessions)")).fetchall()
        }

    assert row is not None
    assert slots_row is not None
    assert "pending_action" in session_columns
    assert "pending_slot_name" in session_columns
