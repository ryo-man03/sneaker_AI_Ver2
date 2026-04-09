from importlib import import_module

from fastapi.testclient import TestClient

app = import_module("app.main").app
client = TestClient(app)


def test_admin_ops_reliability_contract() -> None:
    response = client.get("/api/v1/admin-ops/reliability")
    assert response.status_code == 200

    payload = response.json()
    assert payload["source"].startswith("admin-ops")
    assert "updated_at" in payload
    assert "data" in payload
    assert "db_counts" in payload["data"]
    assert "scheduler" in payload["data"]
    assert "integrations" in payload["data"]
    assert "dqm" in payload["data"]
    assert isinstance(payload["data"]["dqm"]["checks"], list)
