"""The service's one real endpoint — the thing you are operating.

  GET  /items  -> {"items": [...]}
  POST /items  {"name": "..."} -> 201

In-memory on purpose: the briefs on this template are about running and
shipping this service, not about its storage. Persist it only if a ticket
says to, and put the query in app/db.py.
"""
from flask import Blueprint, jsonify, request

bp = Blueprint("items", __name__)

_items: list[dict] = [{"id": 1, "name": "first item"}]


@bp.get("/items")
def list_items():
    return jsonify(items=_items), 200


# The longest name we will store. A cap is not decoration: the list below is
# in memory, so without one a single caller can grow the process until the
# container is OOMKilled and the pod restart-loops.
MAX_NAME = 100


@bp.post("/items")
def create_item():
    # ⚠️ isinstance, NOT `or {}`. A JSON body of `[1]` is truthy and is NOT a
    # dict, so `.get` on it raises AttributeError and gunicorn answers 500 —
    # our bug reported as a server error, for a request that was simply wrong.
    # Whatever validation shape is here gets copied into every project
    # generated from this template, so it checks the TYPE before the value.
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify(error="a JSON object is required"), 400
    name = body.get("name")
    # str(...) would happily accept a dict or a number and store its repr.
    if not isinstance(name, str):
        return jsonify(error="name must be a string"), 400
    name = name.strip()
    if not name or len(name) > MAX_NAME:
        return jsonify(error=f"name must be 1-{MAX_NAME} characters"), 400
    item = {"id": max((i["id"] for i in _items), default=0) + 1, "name": name}
    _items.append(item)
    return jsonify(item), 201
