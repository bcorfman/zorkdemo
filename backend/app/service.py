"""Application service for session lifecycle and command execution."""

import base64
from uuid import uuid4

from .contracts import AdventureFactory, SessionRepository


class AdventureService:
    def __init__(
        self,
        repository: SessionRepository,
        adventure_factory: AdventureFactory,
        markdown_renderer,
    ) -> None:
        self._repository = repository
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
        adventure = self._adventure_factory()
        existing_save_data = session["save_data"]
        if existing_save_data:
            adventure.admin_load(base64.b64decode(existing_save_data.encode("ascii")))

        output_markdown = _strip_prompt_markers(adventure.execute(cleaned_command.split()))
        output_html = self._markdown_renderer(output_markdown)
        next_save_data = base64.b64encode(adventure.admin_save()).decode("ascii")
        updated_session = self._repository.set_save_data(session_id, next_save_data)

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
