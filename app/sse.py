"""Server-Sent Events helpers and routes."""
from __future__ import annotations

import json
import time
from queue import Empty, Queue
from typing import Dict, Generator

from flask import Blueprint, Response, jsonify, request, stream_with_context

sse_bp = Blueprint("sse", __name__)

_message_queue: "Queue[Dict[str, object]]" = Queue()


def publish_event(event: str, data: Dict[str, object]) -> None:
    """Queue an event for connected SSE clients."""
    _message_queue.put({
        "event": event,
        "data": data,
        "timestamp": time.time(),
    })


def _format_sse(payload: Dict[str, object]) -> str:
    event_type = payload.get("event", "message")
    data = json.dumps({
        "timestamp": payload.get("timestamp"),
        "data": payload.get("data"),
    })
    return f"event: {event_type}\ndata: {data}\n\n"


def _event_stream(timeout: float = 15.0) -> Generator[str, None, None]:
    """Generator yielding SSE formatted messages."""
    while True:
        try:
            payload = _message_queue.get(timeout=timeout)
        except Empty:
            keepalive = {
                "event": "keepalive",
                "data": {"status": "alive"},
                "timestamp": time.time(),
            }
            yield _format_sse(keepalive)
        else:
            yield _format_sse(payload)


@sse_bp.route("/stream")
def stream() -> Response:
    """Streaming endpoint used by EventSource clients."""
    response = Response(stream_with_context(_event_stream()), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response


@sse_bp.route("/publish", methods=["POST"])
def publish() -> Response:
    """HTTP helper endpoint to push events into the SSE stream."""
    payload = request.get_json(silent=True) or {}
    message = payload.get("message")

    if not message:
        return jsonify({"error": "message is required"}), 400

    event_payload = {"message": message}
    publish_event("message", event_payload)
    return jsonify({"status": "queued", "data": event_payload}), 202


__all__ = ["publish_event", "sse_bp"]
