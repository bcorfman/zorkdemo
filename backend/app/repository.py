"""Session repository backed by existing Peewee models."""

from web.models import AdventureStore, init_db

from .contracts import SessionRepository, SessionRow


class PeeweeSessionRepository(SessionRepository):
    def get_or_create(self, session_id: str) -> tuple[SessionRow, bool]:
        record, created = AdventureStore.get_or_create(session_id=session_id)
        return self._row_from_record(record), created

    def set_save_data(self, session_id: str, save_data: str) -> SessionRow:
        record, _ = AdventureStore.get_or_create(session_id=session_id)
        record.save_data = save_data
        record.save()
        return self._row_from_record(record)

    @staticmethod
    def _row_from_record(record: AdventureStore) -> SessionRow:
        return {
            "session_id": record.session_id,
            "save_data": record.save_data,
            "created_at": record.create_ts.isoformat(),
            "updated_at": record.updated_ts.isoformat(),
        }


def initialize_database(connection_url: str) -> None:
    """Initialize database tables for session storage."""
    init_db(connection_url)
