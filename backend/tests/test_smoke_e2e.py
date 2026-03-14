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

    # Resume session (not created again)
    resumed_session = client.post("/api/v1/session", json={"session_id": session_id})
    assert resumed_session.status_code == 200
    assert resumed_session.json()["created"] is False

    # Reset session
    reset_result = client.post("/api/v1/session/reset", json={"session_id": session_id})
    assert reset_result.status_code == 200
    assert reset_result.json() == {"session_id": session_id, "reset": True}

    # After reset, inventory should be empty
    inventory_after_reset = client.post(
        "/api/v1/command",
        json={"session_id": session_id, "command": "inventory"},
    )
    assert inventory_after_reset.status_code == 200
    assert "empty" in inventory_after_reset.json()["output_html"].lower()
