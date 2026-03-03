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

    assert row is not None
