"""web frontent for Zorkdemo"""

import base64
from uuid import uuid4

from flask import Flask, session, redirect, url_for, request, render_template
import markdown

from adventure.app import Adventure
from .models import AdventureStore, db_wrapper


def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object("web.settings")

    with app.app_context():
        # set global values
        db_wrapper.init_app(app)

    return app


app = create_app()


@app.route("/")
def index():
    """homepage / index page"""
    if "session_id" not in session:
        session["session_id"] = str(uuid4())
    _, created = AdventureStore.get_or_create(session_id=session["session_id"])
    starting_text = "resuming session..."
    if created:
        adventure = Adventure()
        starting_text = markdown.markdown(adventure.current_room.description)
    return render_template(
        "index.html", session_id=session["session_id"], starting_text=starting_text
    )


@app.route("/endsession")
def endsession():
    """force the end of a session"""
    session.pop("session_id", None)
    return redirect(url_for("index"))


@app.route("/api", methods=["POST"])
def api():
    """the /api endpoint for getting user input and returning output"""

    if "session_id" not in session:
        # TODO: return a better error to the frontend that they probably need to enable cookies
        return {
            "input": request.json["input"],
            "output": "ERROR... session cookie problem!",
        }

    adventure = Adventure()

    # load state
    if session_data := AdventureStore.get_or_none(session_id=session["session_id"]):
        if session_data.save_data:
            adventure.admin_load(base64.b64decode(session_data.save_data.encode()))

    # execute the command
    _output = adventure.execute(request.json["input"].split())
    output = markdown.markdown(_output)

    # save state
    if session_data:
        session_data.save_data = base64.b64encode(adventure.admin_save()).decode(
            "ascii"
        )
        session_data.save()

    return {
        "input": request.json["input"],
        "output": f"{output}",
    }
