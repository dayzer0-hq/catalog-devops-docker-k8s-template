"""Application factory. Register a new blueprint here; keep routes in their own file."""
import logging

from flask import Flask

from .config import Config


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    # Bound the request body. Flask reads an unbounded one into memory, so
    # without this any caller can push the pod past its 256Mi limit and get it
    # OOMKilled — a denial of service that needs no credentials and no bug.
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
    logging.basicConfig(level=Config.LOG_LEVEL)

    from . import health, items

    app.register_blueprint(health.bp)
    app.register_blueprint(items.bp)
    return app
