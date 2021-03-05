from .models import AdventureStore


class AdventureSessionStore:
    def __init__(self):
        pass

    def get(self, session_id: str) -> dict:
        print('get called')
        session_record, _ = AdventureStore.get_or_create(session_id=session_id)
        return session_record.to_json()

    def set(self, session_id: str, session_data: dict):
        print(f'set called: {session_data}')
        session_record, _ = AdventureStore.get_or_create(session_id=session_id)
        session_record.save_data = session_data.get("save_data", "")
        session_record.save()

    def exists(self, session_id: str) -> bool:
        print('exists called')
        return AdventureStore.get_or_none(session_id=session_id) is not None
