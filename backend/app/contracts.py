"""Protocol and typed contracts for backend service boundaries."""

from typing import Protocol, TypedDict


class SessionRow(TypedDict):
    session_id: str
    save_data: str
    pending_action: str | None
    pending_slot_name: str | None
    created_at: str
    updated_at: str


class SessionRepository(Protocol):
    def get_or_create(self, session_id: str) -> tuple[SessionRow, bool]:
        """Get an existing session row or create a new one."""

    def set_save_data(self, session_id: str, save_data: str) -> SessionRow:
        """Persist session save payload and return latest row."""

    def set_pending_confirmation(self, session_id: str, action: str, slot_name: str | None) -> SessionRow:
        """Persist pending confirmation state for a session."""

    def clear_pending_confirmation(self, session_id: str) -> SessionRow:
        """Clear pending confirmation state for a session."""


class SaveSlotRow(TypedDict):
    session_id: str
    slot_name: str
    save_data: str
    created_at: str
    updated_at: str


class SaveSlotRepository(Protocol):
    def has_slot(self, session_id: str, slot_name: str) -> bool:
        """Return whether a slot exists for this session."""

    def upsert_slot(self, session_id: str, slot_name: str, save_data: str) -> SaveSlotRow:
        """Insert or update slot payload for this session."""

    def get_slot(self, session_id: str, slot_name: str) -> SaveSlotRow | None:
        """Get slot payload for this session."""

    def list_slots(self, session_id: str) -> list[SaveSlotRow]:
        """List slots for this session."""

    def delete_all_slots(self, session_id: str) -> int:
        """Delete all slots for this session and return number deleted."""


class AdventureInstance(Protocol):
    def get_intro(self) -> str:
        """Run the game to the first input prompt and return intro text."""

    def execute(self, tokens: list[str]) -> str:
        """Run the parsed command tokens and return markdown output."""

    def admin_save(self) -> bytes:
        """Serialize internal game state."""

    def admin_load(self, input_bytes: bytes) -> None:
        """Deserialize internal game state."""


class AdventureFactory(Protocol):
    def __call__(self) -> AdventureInstance:
        """Create a new adventure instance."""
