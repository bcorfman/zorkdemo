from pathlib import Path

import pytest

from backend.app import dev_runner


class FakeCommandExecutor:
    def __init__(self, run_return_code: int = 0):
        self.run_return_code = run_return_code
        self.run_calls = []
        self.spawn_calls = []

    def run(self, args: list[str], env: dict[str, str], cwd: Path | None = None) -> int:
        self.run_calls.append({"args": args, "env": env, "cwd": cwd})
        return self.run_return_code

    def spawn(self, args: list[str], env: dict[str, str], log_path: Path, cwd: Path | None = None) -> None:
        self.spawn_calls.append({"args": args, "env": env, "cwd": cwd, "log_path": log_path})


def test_healthcheck_url_normalizes_trailing_slash():
    assert dev_runner.healthcheck_url("http://127.0.0.1:8000/") == "http://127.0.0.1:8000/api/v1/health"


def test_ensure_backend_running_restarts_when_healthy(monkeypatch):
    runner = FakeCommandExecutor()
    killed_ports = []
    monkeypatch.setattr(dev_runner, "_kill_process_on_port", lambda port: killed_ports.append(port))
    health_states = iter([True, False, True])

    started = dev_runner.ensure_backend_running(
        backend_url="http://127.0.0.1:8000",
        backend_host="127.0.0.1",
        backend_port=8000,
        database_url="sqlite:///sessions.db",
        cors_allow_origins="http://localhost:5173",
        backend_log=".tmp/backend.log",
        command_executor=runner,
        is_backend_healthy=lambda _: next(health_states),
        sleep_fn=lambda _: None,
        monotonic_fn=lambda: 0.0,
        startup_timeout_seconds=1.0,
        base_env={"PATH": "x"},
    )

    assert started is True
    assert killed_ports == [8000]
    assert len(runner.run_calls) == 1
    assert len(runner.spawn_calls) == 1


def test_ensure_backend_running_runs_migration_and_server():
    runner = FakeCommandExecutor()
    health_states = iter([False, False, True])
    monotonic_states = iter([0.0, 0.1, 0.2])

    started = dev_runner.ensure_backend_running(
        backend_url="http://127.0.0.1:8000",
        backend_host="127.0.0.1",
        backend_port=8000,
        database_url="sqlite:///sessions.db",
        cors_allow_origins="http://localhost:5173",
        backend_log=".tmp/backend.log",
        command_executor=runner,
        is_backend_healthy=lambda _: next(health_states),
        sleep_fn=lambda _: None,
        monotonic_fn=lambda: next(monotonic_states),
        startup_timeout_seconds=1.0,
        base_env={"PATH": "x"},
    )

    assert started is True
    assert len(runner.run_calls) == 1
    assert len(runner.spawn_calls) == 1
    assert runner.run_calls[0]["args"] == ["uv", "run", "alembic", "-c", "backend/alembic.ini", "upgrade", "head"]
    assert runner.spawn_calls[0]["args"] == [
        "uv",
        "run",
        "uvicorn",
        "backend.app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
    ]


def test_ensure_backend_running_raises_on_failed_migration():
    runner = FakeCommandExecutor(run_return_code=1)

    with pytest.raises(RuntimeError, match="Database migration failed"):
        dev_runner.ensure_backend_running(
            backend_url="http://127.0.0.1:8000",
            backend_host="127.0.0.1",
            backend_port=8000,
            database_url="sqlite:///sessions.db",
            cors_allow_origins="http://localhost:5173",
            backend_log=".tmp/backend.log",
            command_executor=runner,
            is_backend_healthy=lambda _: False,
            sleep_fn=lambda _: None,
            monotonic_fn=lambda: 0.0,
            startup_timeout_seconds=1.0,
            base_env={"PATH": "x"},
        )


def test_run_frontend_dev_passes_env_and_args():
    runner = FakeCommandExecutor()
    return_code = dev_runner.run_frontend_dev(
        frontend_dir="frontend",
        api_base_url="http://127.0.0.1:8000",
        frontend_host="127.0.0.1",
        frontend_port=5173,
        command_executor=runner,
        base_env={"PATH": "x"},
    )

    assert return_code == 0
    assert runner.run_calls[0]["cwd"] == Path("frontend")
    assert runner.run_calls[0]["env"]["VITE_API_BASE_URL"] == "http://127.0.0.1:8000"
    assert runner.run_calls[0]["args"] == [
        "npm",
        "run",
        "dev",
        "--",
        "--host",
        "127.0.0.1",
        "--port",
        "5173",
    ]
