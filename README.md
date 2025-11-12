# Flask SSE REST Sample

A minimal Flask application demonstrating REST endpoints and Server-Sent Events
(SSE) with a small front-end powered by vanilla JavaScript.

## Features

- Application factory compatible with Gunicorn (`gunicorn "app:create_app()"`).
- REST API endpoints for health checks and publishing messages.
- Server-Sent Events stream that replays each published message three times at one-second intervals before closing the connection.
- Front-end automatically opens a short-lived SSE connection per submitted message and closes it when the `close` event arrives.
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
flask run --debug --with-threads
```

> **Why `--with-threads`?**  
> The SSE demo keeps the `/stream` connection open while it waits for REST
> messages so it can replay them three times. If you run the built-in Flask
> development server without threading, that long-lived connection will occupy
> the only worker and other endpoints such as `POST /api/messages` will appear
> to “pend” forever. Starting the server with the `--with-threads` flag (or
> using Gunicorn) ensures there is at least one free worker to process REST
> calls while the SSE stream stays open.

### Gunicorn

```bash
gunicorn "app:create_app()" -c gunicorn.conf.py --workers 5
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

In a separate terminal you can watch the SSE burst unfold:

```bash
curl -N http://localhost:8000/stream
```

Every time you `POST /api/messages`, the connected SSE client receives the message three times (one second apart) and the server closes the stream, allowing clients to reconnect cleanly for the next event.
Each stream ends with a `close` event so the front-end automatically tears down the EventSource. Submitting another message opens a fresh connection for the next 3-event burst.
Open the front-end in your browser at [http://localhost:8000](http://localhost:8000)
to watch the real-time activity feed update as messages arrive.
