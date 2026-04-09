# file: tests/test_core_data.py
from importlib import import_module

from fastapi.testclient import TestClient

app = import_module("app.main").app
client = TestClient(app)


def test_sneakers_endpoint() -> None:
    response = client.get("/api/v1/sneakers")
    assert response.status_code == 200
    payload = response.json()
    assert payload["items"]
    assert payload["meta"]["source"]
    assert "updated_at" in payload["meta"]


def test_search_endpoint() -> None:
    response = client.get("/api/v1/search", params={"q": "Jordan"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= 1
    assert payload["items"][0]["rank"] >= 0


def test_market_endpoint() -> None:
    response = client.get("/api/v1/market", params={"period": "1d"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["items"]
    assert "spread_pct" in payload["items"][0]


def test_stocks_endpoint() -> None:
    response = client.get("/api/v1/stocks", params={"period": "1d"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["items"]
    assert payload["correlations_summary"]
