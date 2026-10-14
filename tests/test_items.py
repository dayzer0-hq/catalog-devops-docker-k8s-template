from app import create_app


def test_list_and_create():
    client = create_app().test_client()

    assert client.get("/items").status_code == 200

    created = client.post("/items", json={"name": "a widget"})
    assert created.status_code == 201
    assert created.get_json()["name"] == "a widget"

    names = [i["name"] for i in client.get("/items").get_json()["items"]]
    assert "a widget" in names


def test_create_rejects_a_missing_name():
    res = create_app().test_client().post("/items", json={})
    assert res.status_code == 400


def test_a_json_array_body_is_refused_not_a_500():
    """⚠️ KNOWN-POSITIVE FOR THE isinstance CHECK IN create_item.

    `request.get_json(silent=True) or {}` returns the list unchanged for a body
    of `[1]` — it is truthy — and `.get` on a list raises AttributeError, which
    gunicorn answers as 500. That reports OUR bug as a server error for a
    request that was merely malformed. Revert the isinstance check and this
    test goes red with a 500.
    """
    r = create_app().test_client().post("/items", json=[1])
    assert r.status_code == 400, f"a JSON array answered {r.status_code}, not 400"


def test_an_over_long_name_is_refused():
    r = create_app().test_client().post("/items", json={"name": "x" * 101})
    assert r.status_code == 400


def test_a_non_string_name_is_refused():
    """str(body.get("name")) would accept this and store the dict's repr."""
    r = create_app().test_client().post("/items", json={"name": {"not": "a string"}})
    assert r.status_code == 400
