"""Cross-platform local development launcher for backend + frontend."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from typing import Protocol
from urllib.error import URLError
from urllib.request import urlopen


class CommandExecutor(Protocol):
    def run(self, args: list[str], env: dict[str, str], cwd: Path | None = None) -> int:
        """Run a command and return its process exit code."""

    def spawn(self, args: list[str], env: dict[str, str], log_path: Path, cwd: Path | None = None) -> None:
        """Spawn a detached process writing output to ``log_path``."""


class SubprocessCommandExecutor:
    def run(self, args: list[str], env: dict[str, str], cwd: Path | None = None) -> int:
        completed = subprocess.run(args, env=env, cwd=cwd, check=False)
        return completed.returncode

    def spawn(self, args: list[str], env: dict[str, str], log_path: Path, cwd: Path | None = None) -> None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as log_file:
            subprocess.Popen(  # noqa: S603
                args,
                env=env,
                cwd=cwd,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )


def healthcheck_url(backend_url: str) -> str:
    return f"{backend_url.rstrip('/')}/api/v1/health"


def is_backend_healthy(backend_url: str, timeout_seconds: float = 2.0) -> bool:
    try:
        with urlopen(healthcheck_url(backend_url), timeout=timeout_seconds) as response:
            return response.status == 200
    except URLError:
        return False


def _with_backend_env(base_env: dict[str, str], database_url: str, cors_allow_origins: str) -> dict[str, str]:
    env = dict(base_env)
    env["DATABASE_URL"] = database_url
    env["CORS_ALLOW_ORIGINS"] = cors_allow_origins
    return env


def _kill_process_on_port(port: int) -> None:
    """Kill any process listening on the given port."""
    import signal

    try:
        result = subprocess.run(
            ["lsof", "-ti", f"tcp:{port}"],
            capture_output=True,
            text=True,
            check=False,
        )
        pids = result.stdout.strip().split()
        for pid in pids:
            if pid:
                os.kill(int(pid), signal.SIGTERM)
    except (OSError, ValueError):
        pass


def ensure_backend_running(
    *,
    backend_url: str,
    backend_host: str,
    backend_port: int,
    database_url: str,
    cors_allow_origins: str,
    backend_log: str,
    command_executor: CommandExecutor,
    is_backend_healthy,
    sleep_fn,
    monotonic_fn,
    startup_timeout_seconds: float,
    base_env: dict[str, str],
) -> bool:
    if is_backend_healthy(backend_url):
        _kill_process_on_port(backend_port)
        sleep_fn(0.5)

    env = _with_backend_env(base_env, database_url, cors_allow_origins)
    migrate_args = ["uv", "run", "alembic", "-c", "backend/alembic.ini", "upgrade", "head"]
    migrate_return_code = command_executor.run(migrate_args, env=env)
    if migrate_return_code != 0:
        raise RuntimeError("Database migration failed before backend startup")

    server_args = [
        "uv",
        "run",
        "uvicorn",
        "backend.app.main:app",
        "--host",
        backend_host,
        "--port",
        str(backend_port),
    ]
    command_executor.spawn(server_args, env=env, log_path=Path(backend_log))

    deadline = monotonic_fn() + startup_timeout_seconds
    while monotonic_fn() < deadline:
        if is_backend_healthy(backend_url):
            return True
        sleep_fn(0.25)

    raise RuntimeError(f"Backend failed to start. See {backend_log}")


def open_frontend_url(frontend_url: str) -> None:
    webbrowser.open_new_tab(frontend_url)


def run_frontend_dev(
    *,
    frontend_dir: str,
    api_base_url: str,
    frontend_host: str,
    frontend_port: int,
    command_executor: CommandExecutor,
    base_env: dict[str, str],
) -> int:
    env = dict(base_env)
    env["VITE_API_BASE_URL"] = api_base_url
    args = ["npm", "run", "dev", "--", "--host", frontend_host, "--port", str(frontend_port)]
    return command_executor.run(args, env=env, cwd=Path(frontend_dir))


def _port_arg(value: str) -> int:
    port = int(value)
    if port < 1 or port > 65535:
        raise argparse.ArgumentTypeError("Port must be between 1 and 65535")
    return port


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Cross-platform local dev launcher")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ensure_backend = subparsers.add_parser("ensure-backend", help="Run migration and boot backend if needed")
    ensure_backend.add_argument("--backend-url", required=True)
    ensure_backend.add_argument("--backend-host", required=True)
    ensure_backend.add_argument("--backend-port", required=True, type=_port_arg)
    ensure_backend.add_argument("--database-url", required=True)
    ensure_backend.add_argument("--cors-allow-origins", required=True)
    ensure_backend.add_argument("--backend-log", required=True)
    ensure_backend.add_argument("--startup-timeout-seconds", type=float, default=10.0)

    open_browser = subparsers.add_parser("open-browser", help="Open frontend URL in browser")
    open_browser.add_argument("--frontend-url", required=True)

    frontend = subparsers.add_parser("run-frontend", help="Run frontend dev server")
    frontend.add_argument("--frontend-dir", default="frontend")
    frontend.add_argument("--api-base-url", required=True)
    frontend.add_argument("--frontend-host", required=True)
    frontend.add_argument("--frontend-port", required=True, type=_port_arg)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    command_executor = SubprocessCommandExecutor()
    base_env = dict(os.environ)

    if args.command == "ensure-backend":
        ensure_backend_running(
            backend_url=args.backend_url,
            backend_host=args.backend_host,
            backend_port=args.backend_port,
            database_url=args.database_url,
            cors_allow_origins=args.cors_allow_origins,
            backend_log=args.backend_log,
            command_executor=command_executor,
            is_backend_healthy=is_backend_healthy,
            sleep_fn=time.sleep,
            monotonic_fn=time.monotonic,
            startup_timeout_seconds=args.startup_timeout_seconds,
            base_env=base_env,
        )
        return 0

    if args.command == "open-browser":
        open_frontend_url(args.frontend_url)
        return 0

    if args.command == "run-frontend":
        return run_frontend_dev(
            frontend_dir=args.frontend_dir,
            api_base_url=args.api_base_url,
            frontend_host=args.frontend_host,
            frontend_port=args.frontend_port,
            command_executor=command_executor,
            base_env=base_env,
        )

    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
