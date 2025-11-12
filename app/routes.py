"""REST API and front-end routes."""
from flask import Blueprint, jsonify, render_template, request

from .sse import publish_event


main_bp = Blueprint("main", __name__)
api_bp = Blueprint("api", __name__, url_prefix="/api")


@main_bp.route("/")
def index():
    """Serve the demo front-end."""
    return render_template("index.html")


@api_bp.get("/ping")
def ping():
    """Simple heartbeat endpoint used by the front-end."""
    return jsonify({"status": "ok", "message": "pong"})


@api_bp.post("/messages")
def post_message():
    """Accept a message payload and broadcast it via SSE."""
    payload = request.get_json(silent=True) or {}
    message = payload.get("message")

    if not message:
        return jsonify({"error": "message is required"}), 400

    event_payload = {"message": message}
    publish_event("message", event_payload)

    return jsonify({"status": "accepted", "data": event_payload}), 201
