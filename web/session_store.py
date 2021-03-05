from .models import AdventureStore


class AdventureSessionStore:
    def __init__(self):
        pass

    def get(self, session_id: str) -> dict:
        session_record, _ = AdventureStore.get_or_create(session_id=session_id)
        return session_record.to_json()

    def set(self, session_id: str, session_data: dict):
        session_record, _ = AdventureStore.get_or_create(session_id=session_id)
        session_record.save_data = session_data.get("save_data", "")
        session_record.save()

    def exists(self, session_id: str) -> bool:
        return AdventureStore.get_or_none(session_id=session_id) is not None
