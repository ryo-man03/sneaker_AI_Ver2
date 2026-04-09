from importlib import import_module

from fastapi.testclient import TestClient

app = import_module("app.main").app
client = TestClient(app)


def test_health_has_security_headers() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers.get("x-content-type-options") == "nosniff"
    assert response.headers.get("x-frame-options") == "DENY"
    assert response.headers.get("referrer-policy") == "no-referrer"
    assert response.headers.get("cache-control") == "no-store"


def test_admin_ops_contains_hardening_snapshot() -> None:
    response = client.get("/api/v1/admin-ops/reliability")
    assert response.status_code == 200

    payload = response.json()
    hardening = payload["data"]["hardening"]
    assert hardening["lifespan_mode"] == "enabled"
    assert isinstance(hardening["security_headers_enabled"], bool)
    assert isinstance(hardening["trusted_hosts"], list)

    maintenance = payload["data"]["maintenance"]
    assert isinstance(maintenance["key_rotation_days"], int)
    assert isinstance(maintenance["dependency_audit_days"], int)
    assert isinstance(maintenance["release_channel"], str)
