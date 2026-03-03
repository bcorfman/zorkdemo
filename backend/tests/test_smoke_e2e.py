from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.main import create_app


class SmokeSettings:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.cors_allow_origins = ["http://localhost:5173"]


def test_play_resume_and_reset_flow(tmp_path: Path):
    database_url = f"sqlite+pysqlite:///{tmp_path / 'smoke.db'}"
    app = create_app(settings=SmokeSettings(database_url))
    client = TestClient(app)

    create_result = client.post("/api/v1/session", json={})
    assert create_result.status_code == 200
    first_session = create_result.json()
    session_id = first_session["session_id"]
    assert first_session["created"] is True

    opened_mailbox = client.post(
        "/api/v1/command",
        json={"session_id": session_id, "command": "open mailbox"},
    )
    assert opened_mailbox.status_code == 200

    took_leaflet = client.post(
        "/api/v1/command",
        json={"session_id": session_id, "command": "take leaflet"},
    )
    assert took_leaflet.status_code == 200
    assert "Taken" in took_leaflet.json()["output_html"]

    inventory_after_take = client.post(
        "/api/v1/command",
        json={"session_id": session_id, "command": "inventory"},
    )
    assert inventory_after_take.status_code == 200
    assert "holding a small leaflet" in inventory_after_take.json()["output_html"]

    resumed_session = client.post("/api/v1/session", json={"session_id": session_id})
    assert resumed_session.status_code == 200
    assert resumed_session.json() == {"session_id": session_id, "created": False}

    reset_result = client.post("/api/v1/session/reset", json={"session_id": session_id})
    assert reset_result.status_code == 200
    assert reset_result.json() == {"session_id": session_id, "reset": True}

    inventory_after_reset = client.post(
        "/api/v1/command",
        json={"session_id": session_id, "command": "inventory"},
    )
    assert inventory_after_reset.status_code == 200
    assert "empty handed" in inventory_after_reset.json()["output_html"]
