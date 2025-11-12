"""Server-Sent Events helpers and routes."""
from __future__ import annotations

import json
import time
from queue import Queue
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


def _timed_burst(payload: Dict[str, object], burst_count: int, interval: float) -> Generator[str, None, None]:
    """Yield the same payload multiple times with a delay in between."""
    base_event = payload.get("event", "message")
    raw_data = payload.get("data")
    base_data = raw_data if isinstance(raw_data, dict) else {"value": raw_data}

    for index in range(burst_count):
        burst_payload = {
            "event": base_event,
            "data": {
                **base_data,
                "sequence": index + 1,
                "total": burst_count,
                "remaining": burst_count - index - 1,
            },
            "timestamp": time.time(),
        }
        yield _format_sse(burst_payload)

        if index < burst_count - 1:
            time.sleep(interval)


def _event_stream(burst_count: int = 3, interval: float = 1.0) -> Generator[str, None, None]:
    """Generator that streams a single event in fixed intervals, then closes."""
    handshake = {
        "event": "keepalive",
        "data": {"status": "connected"},
        "timestamp": time.time(),
    }
    yield _format_sse(handshake)

    payload = _message_queue.get()
    yield from _timed_burst(payload, burst_count, interval)

    closing_payload = {
        "event": "close",
        "data": {"status": "complete"},
        "timestamp": time.time(),
    }
    final_data = payload.get("data")
    if isinstance(final_data, dict) and "message" in final_data:
        closing_payload["data"]["message"] = final_data["message"]

    yield _format_sse(closing_payload)


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
