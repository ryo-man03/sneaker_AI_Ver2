# file: tests/test_health.py
from importlib import import_module

from fastapi.testclient import TestClient

app = import_module("app.main").app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert "service" in payload
