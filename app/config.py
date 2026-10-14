"""Every environment variable this service reads, in one place.

Nothing here has a secret in it. The defaults are safe for local development
only; production values come from the environment (see README).
"""
import os


class Config:
    # Where gunicorn/Flask listens. The container EXPOSEs this.
    PORT = int(os.environ.get("PORT", "8080"))

    # "development" | "production". Only used for log verbosity today.
    APP_ENV = os.environ.get("APP_ENV", "development")

    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

    # postgresql://user:password@host:5432/dbname
    # Unset is a supported state: /readyz then reports the database as
    # unconfigured rather than pretending it is reachable.
    DATABASE_URL = os.environ.get("DATABASE_URL", "")

    # Seconds to wait for the database on a readiness check. Kept short: a
    # readiness probe that hangs is a pod that never leaves Terminating.
    DB_CONNECT_TIMEOUT = int(os.environ.get("DB_CONNECT_TIMEOUT", "2"))
