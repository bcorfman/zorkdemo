"""Session and save-slot repositories."""

from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import sessionmaker

from .contracts import SaveSlotRepository, SaveSlotRow, SessionRepository, SessionRow
from .db import AdventureSaveSlot, AdventureSession


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

    def set_pending_confirmation(self, session_id: str, action: str, slot_name: str | None) -> SessionRow:
        with self._session_factory() as db_session:
            record = db_session.get(AdventureSession, session_id)
            if record is None:
                record = AdventureSession(
                    session_id=session_id,
                    save_data="",
                    pending_action=action,
                    pending_slot_name=slot_name,
                )
                db_session.add(record)
            else:
                record.pending_action = action
                record.pending_slot_name = slot_name
                record.updated_at = datetime.utcnow()

            db_session.commit()
            db_session.refresh(record)
            return self._row_from_record(record)

    def clear_pending_confirmation(self, session_id: str) -> SessionRow:
        with self._session_factory() as db_session:
            record = db_session.get(AdventureSession, session_id)
            if record is None:
                record = AdventureSession(session_id=session_id, save_data="", pending_action=None, pending_slot_name=None)
                db_session.add(record)
            else:
                record.pending_action = None
                record.pending_slot_name = None
                record.updated_at = datetime.utcnow()

            db_session.commit()
            db_session.refresh(record)
            return self._row_from_record(record)

    @staticmethod
    def _row_from_record(record: AdventureSession) -> SessionRow:
        return {
            "session_id": record.session_id,
            "save_data": record.save_data,
            "pending_action": record.pending_action,
            "pending_slot_name": record.pending_slot_name,
            "created_at": record.created_at.isoformat(),
            "updated_at": record.updated_at.isoformat(),
        }


class PostgresSaveSlotRepository(SaveSlotRepository):
    def __init__(self, session_factory: sessionmaker):
        self._session_factory = session_factory

    def has_slot(self, session_id: str, slot_name: str) -> bool:
        with self._session_factory() as db_session:
            record = db_session.get(AdventureSaveSlot, {"session_id": session_id, "slot_name": slot_name})
            return record is not None

    def upsert_slot(self, session_id: str, slot_name: str, save_data: str) -> SaveSlotRow:
        with self._session_factory() as db_session:
            record = db_session.get(AdventureSaveSlot, {"session_id": session_id, "slot_name": slot_name})
            if record is None:
                record = AdventureSaveSlot(session_id=session_id, slot_name=slot_name, save_data=save_data)
                db_session.add(record)
            else:
                record.save_data = save_data
                record.updated_at = datetime.utcnow()

            db_session.commit()
            db_session.refresh(record)
            return self._row_from_record(record)

    def get_slot(self, session_id: str, slot_name: str) -> SaveSlotRow | None:
        with self._session_factory() as db_session:
            record = db_session.get(AdventureSaveSlot, {"session_id": session_id, "slot_name": slot_name})
            if record is None:
                return None
            return self._row_from_record(record)

    def list_slots(self, session_id: str) -> list[SaveSlotRow]:
        with self._session_factory() as db_session:
            records = db_session.execute(
                select(AdventureSaveSlot)
                .where(AdventureSaveSlot.session_id == session_id)
                .order_by(AdventureSaveSlot.slot_name.asc())
            ).scalars()
            return [self._row_from_record(record) for record in records]

    def delete_all_slots(self, session_id: str) -> int:
        with self._session_factory() as db_session:
            result = db_session.execute(delete(AdventureSaveSlot).where(AdventureSaveSlot.session_id == session_id))
            db_session.commit()
            return result.rowcount or 0

    @staticmethod
    def _row_from_record(record: AdventureSaveSlot) -> SaveSlotRow:
        return {
            "session_id": record.session_id,
            "slot_name": record.slot_name,
            "save_data": record.save_data,
            "created_at": record.created_at.isoformat(),
            "updated_at": record.updated_at.isoformat(),
        }
