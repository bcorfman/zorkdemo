from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.main import create_app

STORY_PATH = str(Path(__file__).resolve().parent.parent.parent / "data" / "zork1.z3")


class SmokeSettings:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.cors_allow_origins = ["http://localhost:5173"]
        self.story_file = STORY_PATH


def test_play_resume_and_reset_flow(tmp_path: Path):
    database_url = f"sqlite+pysqlite:///{tmp_path / 'smoke.db'}"
    app = create_app(settings=SmokeSettings(database_url))
    client = TestClient(app)

    # Create session — should return intro text
    create_result = client.post("/api/v1/session", json={})
    assert create_result.status_code == 200
    first_session = create_result.json()
    session_id = first_session["session_id"]
    assert first_session["created"] is True
    assert "West of House" in first_session["intro_html"]

    # Open the mailbox
    opened_mailbox = client.post(
        "/api/v1/command",
        json={"session_id": session_id, "command": "open mailbox"},
    )
    assert opened_mailbox.status_code == 200
    assert "Opening the" in opened_mailbox.json()["output_html"]
    assert "small mailbox" in opened_mailbox.json()["output_html"]

    # Take the leaflet
    took_leaflet = client.post(
        "/api/v1/command",
        json={"session_id": session_id, "command": "take leaflet"},
    )
    assert took_leaflet.status_code == 200
    assert "Taken" in took_leaflet.json()["output_html"]

    # Check inventory
    inventory_after_take = client.post(
        "/api/v1/command",
        json={"session_id": session_id, "command": "inventory"},
    )
    assert inventory_after_take.status_code == 200
    assert "leaflet" in inventory_after_take.json()["output_html"].lower()

    # Save a named slot and verify listing
    save_slot = client.post(
        "/api/v1/command",
        json={"session_id": session_id, "command": "save SLOT1"},
    )
    assert save_slot.status_code == 200
    assert save_slot.json()["output_html"] == "<p>SLOT1 saved.</p>"

    list_slots = client.post(
        "/api/v1/command",
        json={"session_id": session_id, "command": "save"},
    )
    assert list_slots.status_code == 200
    assert "SLOT1" in list_slots.json()["output_html"]

    # Restore requires confirmation, and non-Y/N commands are blocked until answered
    restore_prompt = client.post(
        "/api/v1/command",
        json={"session_id": session_id, "command": "restore SLOT1"},
    )
    assert restore_prompt.status_code == 200
    assert "Do you wish to restore over the game in progress (Y/N)?" in restore_prompt.json()["output_html"]

    blocked = client.post(
        "/api/v1/command",
        json={"session_id": session_id, "command": "look"},
    )
    assert blocked.status_code == 200
    assert blocked.json()["output_html"] == "<p>Please answer Y or N.</p>"

    restore_confirm = client.post(
        "/api/v1/command",
        json={"session_id": session_id, "command": "Y"},
    )
    assert restore_confirm.status_code == 200
    assert restore_confirm.json()["output_html"] == "<p>SLOT1 restored.</p>"

    # Resume session (not created again)
    resumed_session = client.post("/api/v1/session", json={"session_id": session_id})
    assert resumed_session.status_code == 200
    assert resumed_session.json()["created"] is False

    # Reset session
    reset_result = client.post("/api/v1/session/reset", json={"session_id": session_id})
    assert reset_result.status_code == 200
    assert reset_result.json()["session_id"] == session_id
    assert reset_result.json()["reset"] is True
    assert "West of House" in reset_result.json()["intro_html"]

    # Reset slots requires confirmation and only affects this session
    reset_slots_prompt = client.post(
        "/api/v1/command",
        json={"session_id": session_id, "command": "reset slots"},
    )
    assert reset_slots_prompt.status_code == 200
    assert "Do you wish to delete all saved slots for this session (Y/N)?" in reset_slots_prompt.json()["output_html"]

    reset_slots_cancelled = client.post(
        "/api/v1/command",
        json={"session_id": session_id, "command": "N"},
    )
    assert reset_slots_cancelled.status_code == 200
    assert reset_slots_cancelled.json()["output_html"] == "<p>Reset slots cancelled.</p>"

    client.post("/api/v1/command", json={"session_id": session_id, "command": "reset slots"})
    reset_slots_confirmed = client.post(
        "/api/v1/command",
        json={"session_id": session_id, "command": "Y"},
    )
    assert reset_slots_confirmed.status_code == 200
    assert reset_slots_confirmed.json()["output_html"] == "<p>All saved slots deleted for this session.</p>"

    # After reset, inventory should be empty
    inventory_after_reset = client.post(
        "/api/v1/command",
        json={"session_id": session_id, "command": "inventory"},
    )
    assert inventory_after_reset.status_code == 200
    assert "empty" in inventory_after_reset.json()["output_html"].lower()
