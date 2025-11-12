# Flask SSE REST Sample

A minimal Flask application demonstrating REST endpoints and Server-Sent Events
(SSE) with a small front-end powered by vanilla JavaScript.

## Features

- Application factory compatible with Gunicorn (`gunicorn "app:create_app()"`).
- REST API endpoints for health checks and publishing messages.
- Server-Sent Events stream backed by an in-memory queue.
- Lightweight HTML/CSS/JS front-end that interacts with the API and SSE stream.

## Requirements

- Python 3.10+
- Virtualenv (recommended)

Install dependencies with:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the App

### Flask development server

```bash
export FLASK_APP="app:create_app"
flask run --debug
```

### Gunicorn

```bash
gunicorn "app:create_app()" -c gunicorn.conf.py
```

The server exposes:

- `GET /` – Front-end demo page.
- `GET /api/ping` – Health check endpoint.
- `POST /api/messages` – Accepts `{ "message": "..." }` and broadcasts to SSE clients.
- `GET /stream` – SSE endpoint consumed by the browser via `EventSource`.
- `POST /publish` – Helper endpoint to push SSE messages without using the REST API.

## Example Usage

Use `curl` to try the REST and SSE interactions:

```bash
curl http://localhost:8000/api/ping
curl -X POST http://localhost:8000/api/messages \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from curl"}'
```

Open the front-end in your browser at [http://localhost:8000](http://localhost:8000)
to watch the real-time activity feed update as messages arrive.
