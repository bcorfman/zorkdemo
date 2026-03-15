"""FastAPI routes for the v1 backend API."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .service import AdventureService


class HealthResponse(BaseModel):
    status: str


class SessionCreateRequest(BaseModel):
    session_id: str | None = None


class SessionCreateResponse(BaseModel):
    session_id: str
    created: bool
    intro_html: str = ""


class CommandRequest(BaseModel):
    session_id: str
    command: str


class CommandResponse(BaseModel):
    session_id: str
    input: str
    output_html: str
    updated_at: str


class SessionResetRequest(BaseModel):
    session_id: str


class SessionResetResponse(BaseModel):
    session_id: str
    reset: bool
    intro_html: str = ""


def create_api_router(service: AdventureService) -> APIRouter:
    router = APIRouter(prefix="/api/v1", tags=["api"])

    @router.get("/health", response_model=HealthResponse)
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    @router.post("/session", response_model=SessionCreateResponse)
    def create_session(payload: SessionCreateRequest) -> dict[str, str | bool]:
        return service.create_session(payload.session_id)

    @router.post("/command", response_model=CommandResponse)
    def execute_command(payload: CommandRequest) -> dict[str, str]:
        try:
            return service.execute_command(
                session_id=payload.session_id,
                command=payload.command,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.post("/session/reset", response_model=SessionResetResponse)
    def reset_session(payload: SessionResetRequest) -> dict[str, str | bool]:
        return service.reset_session(payload.session_id)

    return router
