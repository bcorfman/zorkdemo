import base64

import hug

from adventure.app import Adventure
from adventure.output import MarkdownPassthru

from .models import init_db
from .session_store import AdventureSessionStore
from .settings import settings
from .template_loader import get_template
from .utils import markdown2html

html = hug.get(output=hug.output_format.html)
api = hug.API(__name__)
api.http.add_middleware(
    hug.middleware.SessionMiddleware(
        AdventureSessionStore(), cookie_secure=False, cookie_http_only=False
    )
)
init_db(settings.DATABASE_URL)


@hug.get("/HEALTH-CHECK")
def health_check():
    """simple health status check page"""
    return {"status": "okay"}


@html.urls("/")
def index(session: hug.directives.session):
    """main index / page"""
    starting_text = ""
    if not session:
        starting_text = markdown2html(
            Adventure(output_strategy=MarkdownPassthru()).current_room.description
        )
    else:
        starting_text = f"Resuming (session: {session.get('session_id')})"
    return get_template("index.html").render(session_id="", starting_text=starting_text)


@hug.post("/api")
def adventure_api(session: hug.directives.session, input_data: str):
    """the /api endpoint for XMLHttpRequest handling"""
    adventure = Adventure(output_strategy=MarkdownPassthru())
    if session and session.get("save_data"):
        adventure.admin_load(base64.b64decode(session["save_data"].encode()))
    _output = markdown2html(adventure.execute(input_data.split()))
    session["save_data"] = base64.b64encode(adventure.admin_save()).decode("ascii")
    return {"input": input_data, "output": _output}


@html.urls("/endsession")
def end_session(session: hug.directives.session):
    """endpoint to end the current session"""
    # TODO: delete session data
    hug.redirect.to("/")
