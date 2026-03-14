"""FastAPI application factory and wiring."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from yazm.web_adapter import ZorkWebAdapter

from .api import create_api_router
from .db import create_session_factory, initialize_database
from .repository import PostgresSessionRepository
from .rendering import markdown_to_html
from .service import AdventureService
from .settings import Settings, settings as default_settings

_DEFAULT_STORY_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "zork1.z3"


def _load_story_data(settings: Settings) -> bytes:
    path = Path(settings.story_file) if settings.story_file else _DEFAULT_STORY_PATH
    if not path.exists():
        raise FileNotFoundError(f"Story file not found: {path}. Set STORY_FILE env var or place zork1.z3 in data/.")
    return path.read_bytes()


def _make_adventure_factory(story_data: bytes):
    def factory() -> ZorkWebAdapter:
        return ZorkWebAdapter(story_data)
    return factory


def create_app(
    *,
    settings: Settings | None = None,
    service: AdventureService | None = None,
    init_database_on_startup: bool = True,
) -> FastAPI:
    app_settings = settings or default_settings

    if init_database_on_startup:
        initialize_database(app_settings.database_url)

    if service is None:
        story_data = _load_story_data(app_settings)
        session_factory = create_session_factory(app_settings.database_url)
        repository = PostgresSessionRepository(session_factory)
        service = AdventureService(
            repository=repository,
            adventure_factory=_make_adventure_factory(story_data),
            markdown_renderer=markdown_to_html,
        )

    app = FastAPI(title="zorkdemo backend", version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(create_api_router(service))

    return app


try:
    app = create_app()
except FileNotFoundError:
    # Story file not available (e.g. during test collection).
    # Tests inject their own service via create_app(), so build a
    # minimal app that will fail clearly if actually hit at runtime.
    app = FastAPI(title="zorkdemo backend (no story file)", version="1.0.0")
