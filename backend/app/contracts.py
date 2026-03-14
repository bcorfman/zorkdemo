"""Protocol and typed contracts for backend service boundaries."""

from typing import Protocol, TypedDict


class SessionRow(TypedDict):
    session_id: str
    save_data: str
    created_at: str
    updated_at: str


class SessionRepository(Protocol):
    def get_or_create(self, session_id: str) -> tuple[SessionRow, bool]:
        """Get an existing session row or create a new one."""

    def set_save_data(self, session_id: str, save_data: str) -> SessionRow:
        """Persist session save payload and return latest row."""


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
