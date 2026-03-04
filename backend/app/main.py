"""FastAPI application factory and wiring."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from adventure.app import Adventure
from adventure.output import MarkdownPassthru

from .api import create_api_router
from .db import create_session_factory, initialize_database
from .repository import PostgresSessionRepository
from .rendering import markdown_to_html
from .service import AdventureService
from .settings import Settings, settings as default_settings


def _create_adventure() -> Adventure:
    return Adventure(output_strategy=MarkdownPassthru())


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
        session_factory = create_session_factory(app_settings.database_url)
        repository = PostgresSessionRepository(session_factory)
        service = AdventureService(
            repository=repository,
            adventure_factory=_create_adventure,
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


app = create_app()
