"""SQLAlchemy database definitions and session factory helpers."""

from datetime import datetime

from sqlalchemy import DateTime, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class AdventureSession(Base):
    __tablename__ = "adventure_sessions"

    session_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    save_data: Mapped[str] = mapped_column(String, default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


def normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


def create_session_factory(database_url: str) -> sessionmaker:
    engine = create_engine(normalize_database_url(database_url))
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def initialize_database(database_url: str) -> None:
    engine = create_engine(normalize_database_url(database_url))
    Base.metadata.create_all(engine)
