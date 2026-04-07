# file: tests/test_auth.py
from importlib import import_module

from fastapi.testclient import TestClient

app = import_module("app.main").app

client = TestClient(app)


def test_login_success() -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "yamada@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]


def test_login_failure() -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "yamada@example.com", "password": "wrongpass"},
    )
    assert response.status_code == 401
