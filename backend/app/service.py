"""Application service for session lifecycle and command execution."""

import base64
from uuid import uuid4

from .contracts import AdventureFactory, SaveSlotRepository, SessionRepository, SessionRow

_ACTION_SAVE_OVERWRITE = "save_overwrite"
_ACTION_RESTORE_SLOT = "restore_slot"
_ACTION_RESET_SLOTS = "reset_slots"


class AdventureService:
    def __init__(
        self,
        repository: SessionRepository,
        save_slot_repository: SaveSlotRepository,
        adventure_factory: AdventureFactory,
        markdown_renderer,
    ) -> None:
        self._repository = repository
        self._save_slot_repository = save_slot_repository
        self._adventure_factory = adventure_factory
        self._markdown_renderer = markdown_renderer

    def create_session(self, session_id: str | None) -> dict[str, str | bool]:
        resolved_session_id = session_id or str(uuid4())
        _, created = self._repository.get_or_create(resolved_session_id)
        result: dict[str, str | bool] = {"session_id": resolved_session_id, "created": created}
        if created:
            adventure = self._adventure_factory()
            intro_markdown = _normalize_intro_text(adventure.get_intro())
            result["intro_html"] = self._markdown_renderer(intro_markdown)
            next_save_data = base64.b64encode(adventure.admin_save()).decode("ascii")
            self._repository.set_save_data(resolved_session_id, next_save_data)
        return result

    def execute_command(self, session_id: str, command: str) -> dict[str, str]:
        cleaned_command = command.strip()
        if not cleaned_command:
            raise ValueError("Command must not be empty")

        session, _ = self._repository.get_or_create(session_id)
        tokens = cleaned_command.split()
        command_name = tokens[0].lower()

        pending_action = session["pending_action"]
        if pending_action is not None:
            return self._handle_pending_confirmation(session, cleaned_command)

        if command_name == "save":
            return self._handle_save_command(session, cleaned_command, tokens)
        if command_name == "restore":
            return self._handle_restore_command(session, cleaned_command, tokens)
        if command_name == "reset":
            return self._handle_reset_slots_command(session, cleaned_command, tokens)

        adventure = self._load_adventure_from_session(session)
        output_markdown = _strip_prompt_markers(adventure.execute(tokens))
        next_save_data = base64.b64encode(adventure.admin_save()).decode("ascii")
        updated_session = self._repository.set_save_data(session_id, next_save_data)
        output_html = self._markdown_renderer(output_markdown)

        return {
            "session_id": session_id,
            "input": cleaned_command,
            "output_html": output_html,
            "updated_at": updated_session["updated_at"],
        }

    def reset_session(self, session_id: str) -> dict[str, str | bool]:
        adventure = self._adventure_factory()
        intro_markdown = _normalize_intro_text(adventure.get_intro())
        intro_html = self._markdown_renderer(intro_markdown)
        next_save_data = base64.b64encode(adventure.admin_save()).decode("ascii")
        self._repository.set_save_data(session_id, next_save_data)
        return {"session_id": session_id, "reset": True, "intro_html": intro_html}

    def _handle_pending_confirmation(self, session: SessionRow, cleaned_command: str) -> dict[str, str]:
        answer = cleaned_command.strip().lower()
        if answer == "n":
            pending_action = session["pending_action"]
            updated_session = self._repository.clear_pending_confirmation(session["session_id"])
            cancelled_text = _cancelled_text_for_action(pending_action)
            return self._command_response(
                session["session_id"],
                cleaned_command,
                cancelled_text,
                updated_session["updated_at"],
            )

        if answer != "y":
            return self._command_response(
                session["session_id"],
                cleaned_command,
                "Please answer Y or N.",
                session["updated_at"],
            )

        pending_action = session["pending_action"]
        slot_name = session["pending_slot_name"]

        if pending_action == _ACTION_SAVE_OVERWRITE:
            adventure = self._load_adventure_from_session(session)
            slot_save_data = base64.b64encode(adventure.admin_save()).decode("ascii")
            self._save_slot_repository.upsert_slot(session["session_id"], slot_name or "", slot_save_data)
            updated_session = self._repository.clear_pending_confirmation(session["session_id"])
            return self._command_response(
                session["session_id"],
                cleaned_command,
                f"{slot_name} overwritten.",
                updated_session["updated_at"],
            )

        if pending_action == _ACTION_RESTORE_SLOT:
            slot = self._save_slot_repository.get_slot(session["session_id"], slot_name or "")
            if slot is None:
                updated_session = self._repository.clear_pending_confirmation(session["session_id"])
                return self._command_response(
                    session["session_id"],
                    cleaned_command,
                    f"No saved slot named {slot_name}.",
                    updated_session["updated_at"],
                )

            adventure = self._adventure_factory()
            adventure.admin_load(base64.b64decode(slot["save_data"].encode("ascii")))
            next_save_data = base64.b64encode(adventure.admin_save()).decode("ascii")
            self._repository.set_save_data(session["session_id"], next_save_data)
            updated_session = self._repository.clear_pending_confirmation(session["session_id"])
            return self._command_response(
                session["session_id"],
                cleaned_command,
                f"{slot_name} restored.",
                updated_session["updated_at"],
            )

        if pending_action == _ACTION_RESET_SLOTS:
            self._save_slot_repository.delete_all_slots(session["session_id"])
            updated_session = self._repository.clear_pending_confirmation(session["session_id"])
            return self._command_response(
                session["session_id"],
                cleaned_command,
                "All saved slots deleted for this session.",
                updated_session["updated_at"],
            )

        updated_session = self._repository.clear_pending_confirmation(session["session_id"])
        return self._command_response(
            session["session_id"],
            cleaned_command,
            "Please answer Y or N.",
            updated_session["updated_at"],
        )

    def _handle_save_command(self, session: SessionRow, cleaned_command: str, tokens: list[str]) -> dict[str, str]:
        session_id = session["session_id"]
        if len(tokens) == 1:
            return self._command_response(
                session_id,
                cleaned_command,
                _format_slot_listing(self._list_slot_names(session_id)),
                session["updated_at"],
            )
        if len(tokens) != 2:
            return self._command_response(session_id, cleaned_command, "Usage: save <slot>", session["updated_at"])

        slot_name = tokens[1]
        if self._save_slot_repository.has_slot(session_id, slot_name):
            updated_session = self._repository.set_pending_confirmation(session_id, _ACTION_SAVE_OVERWRITE, slot_name)
            return self._command_response(
                session_id,
                cleaned_command,
                f"{slot_name} already exists. Do you wish to overwrite it (Y/N)?",
                updated_session["updated_at"],
            )

        adventure = self._load_adventure_from_session(session)
        slot_save_data = base64.b64encode(adventure.admin_save()).decode("ascii")
        self._save_slot_repository.upsert_slot(session_id, slot_name, slot_save_data)
        return self._command_response(session_id, cleaned_command, f"{slot_name} saved.", session["updated_at"])

    def _handle_restore_command(self, session: SessionRow, cleaned_command: str, tokens: list[str]) -> dict[str, str]:
        session_id = session["session_id"]
        if len(tokens) == 1:
            return self._command_response(
                session_id,
                cleaned_command,
                _format_slot_listing(self._list_slot_names(session_id)),
                session["updated_at"],
            )
        if len(tokens) != 2:
            return self._command_response(session_id, cleaned_command, "Usage: restore <slot>", session["updated_at"])

        slot_name = tokens[1]
        if not self._save_slot_repository.has_slot(session_id, slot_name):
            return self._command_response(
                session_id,
                cleaned_command,
                f"No saved slot named {slot_name}.",
                session["updated_at"],
            )

        updated_session = self._repository.set_pending_confirmation(session_id, _ACTION_RESTORE_SLOT, slot_name)
        return self._command_response(
            session_id,
            cleaned_command,
            "Do you wish to restore over the game in progress (Y/N)?",
            updated_session["updated_at"],
        )

    def _handle_reset_slots_command(self, session: SessionRow, cleaned_command: str, tokens: list[str]) -> dict[str, str]:
        if len(tokens) == 2 and tokens[1].lower() == "slots":
            updated_session = self._repository.set_pending_confirmation(session["session_id"], _ACTION_RESET_SLOTS, None)
            return self._command_response(
                session["session_id"],
                cleaned_command,
                "Do you wish to delete all saved slots for this session (Y/N)?",
                updated_session["updated_at"],
            )
        return self._command_response(session["session_id"], cleaned_command, "Usage: reset slots", session["updated_at"])

    def _list_slot_names(self, session_id: str) -> list[str]:
        return [row["slot_name"] for row in self._save_slot_repository.list_slots(session_id)]

    def _load_adventure_from_session(self, session: SessionRow):
        adventure = self._adventure_factory()
        existing_save_data = session["save_data"]
        if existing_save_data:
            adventure.admin_load(base64.b64decode(existing_save_data.encode("ascii")))
        return adventure

    def _command_response(
        self,
        session_id: str,
        cleaned_command: str,
        output_markdown: str,
        updated_at: str,
    ) -> dict[str, str]:
        return {
            "session_id": session_id,
            "input": cleaned_command,
            "output_html": self._markdown_renderer(_strip_prompt_markers(output_markdown)),
            "updated_at": updated_at,
        }


def _collapse_immediately_repeated_intro_block(intro_text: str) -> str:
    stripped_intro = intro_text.strip()
    if not stripped_intro:
        return intro_text

    paragraphs = [block.strip() for block in stripped_intro.split("\n\n") if block.strip()]
    if len(paragraphs) < 2:
        return intro_text

    while len(paragraphs) >= 2 and paragraphs[-1] == paragraphs[-2]:
        paragraphs.pop()

    return "\n\n".join(paragraphs)


def _strip_prompt_markers(output_text: str) -> str:
    lines = output_text.splitlines()
    normalized_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == ">":
            continue
        if line.lstrip().startswith(">"):
            first_prompt = line.find(">")
            line = line[first_prompt + 1 :].lstrip()
            if not line:
                continue
        normalized_lines.append(line)
    return "\n".join(normalized_lines).strip()


def _normalize_intro_text(intro_text: str) -> str:
    return _strip_prompt_markers(_collapse_immediately_repeated_intro_block(intro_text))


def _cancelled_text_for_action(action: str | None) -> str:
    if action == _ACTION_SAVE_OVERWRITE:
        return "Overwrite cancelled."
    if action == _ACTION_RESTORE_SLOT:
        return "Restore cancelled."
    if action == _ACTION_RESET_SLOTS:
        return "Reset slots cancelled."
    return "Cancelled."


def _format_slot_listing(slot_names: list[str]) -> str:
    if not slot_names:
        return "No saved slots yet."
    lines = ["Saved slots:"]
    lines.extend(f"- {slot_name}" for slot_name in slot_names)
    return "\n".join(lines)
