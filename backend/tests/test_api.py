from fastapi.testclient import TestClient

from backend.app.main import create_app


class FakeService:
    def create_session(self, session_id):
        return {"session_id": session_id or "generated-session", "created": True, "intro_html": "<p>Welcome</p>"}

    def execute_command(self, session_id, command):
        return {
            "session_id": session_id,
            "input": command,
            "output_html": "<p>hello</p>",
            "updated_at": "2026-01-01T00:00:01",
        }

    def reset_session(self, session_id):
        return {"session_id": session_id, "reset": True}


def test_health_check():
    app = create_app(service=FakeService(), init_database_on_startup=False)
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_session_endpoint():
    app = create_app(service=FakeService(), init_database_on_startup=False)
    client = TestClient(app)

    response = client.post("/api/v1/session", json={})

    assert response.status_code == 200
    assert response.json() == {"session_id": "generated-session", "created": True, "intro_html": "<p>Welcome</p>"}


def test_command_endpoint():
    app = create_app(service=FakeService(), init_database_on_startup=False)
    client = TestClient(app)

    response = client.post(
        "/api/v1/command",
        json={"session_id": "abc123", "command": "look"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "session_id": "abc123",
        "input": "look",
        "output_html": "<p>hello</p>",
        "updated_at": "2026-01-01T00:00:01",
    }


def test_reset_endpoint():
    app = create_app(service=FakeService(), init_database_on_startup=False)
    client = TestClient(app)

    response = client.post("/api/v1/session/reset", json={"session_id": "abc123"})

    assert response.status_code == 200
    assert response.json() == {"session_id": "abc123", "reset": True}
