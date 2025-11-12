"""Application factory for the Flask SSE REST sample."""
from pathlib import Path

from flask import Flask

from .routes import api_bp, main_bp
from .sse import sse_bp

BASE_DIR = Path(__file__).resolve().parent.parent


def create_app() -> Flask:
    """Application factory used by gunicorn."""
    app = Flask(__name__, static_folder=str(BASE_DIR / "static"), template_folder=str(BASE_DIR / "templates"))

    app.config.setdefault("JSON_SORT_KEYS", False)

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(sse_bp)

    return app


__all__ = ["create_app"]
