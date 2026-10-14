from app import create_app


def test_health_is_ok():
    client = create_app().test_client()
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}


def test_readiness_fails_when_no_database_is_configured(monkeypatch):
    # Readiness must report the dependency, not copy liveness.
    from app.config import Config

    monkeypatch.setattr(Config, "DATABASE_URL", "")
    res = create_app().test_client().get("/readyz")
    assert res.status_code == 503
    assert res.get_json()["status"] == "not_ready"
