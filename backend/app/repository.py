"""Session repositories."""

from .contracts import SessionRepository, SessionRow
from .db import AdventureSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime


class PostgresSessionRepository(SessionRepository):
    def __init__(self, session_factory: sessionmaker):
        self._session_factory = session_factory

    def get_or_create(self, session_id: str) -> tuple[SessionRow, bool]:
        with self._session_factory() as db_session:
            record = db_session.get(AdventureSession, session_id)
            if record is not None:
                return self._row_from_record(record), False

            record = AdventureSession(session_id=session_id, save_data="")
            db_session.add(record)
            db_session.commit()
            db_session.refresh(record)
            return self._row_from_record(record), True

    def set_save_data(self, session_id: str, save_data: str) -> SessionRow:
        with self._session_factory() as db_session:
            record = db_session.get(AdventureSession, session_id)
            if record is None:
                record = AdventureSession(session_id=session_id, save_data=save_data)
                db_session.add(record)
            else:
                record.save_data = save_data
                record.updated_at = datetime.utcnow()

            db_session.commit()
            db_session.refresh(record)
            return self._row_from_record(record)

    @staticmethod
    def _row_from_record(record: AdventureSession) -> SessionRow:
        return {
            "session_id": record.session_id,
            "save_data": record.save_data,
            "created_at": record.created_at.isoformat(),
            "updated_at": record.updated_at.isoformat(),
        }
