"""Liveness and readiness. Add or change a probe HERE, nowhere else.

  GET /health  liveness  — is the process alive? No dependencies touched.
  GET /readyz  readiness — can it serve traffic? Checks the database.

They are deliberately separate: a failed liveness probe restarts the pod, and
restarting it will not fix a database that is down.
"""
from flask import Blueprint, jsonify

from . import db

bp = Blueprint("health", __name__)


@bp.get("/health")
def health():
    return jsonify(status="ok"), 200


@bp.get("/readyz")
def readyz():
    ok, detail = db.ping()
    return jsonify(status="ready" if ok else "not_ready", database=detail), (
        200 if ok else 503
    )
