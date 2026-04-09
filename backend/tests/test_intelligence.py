# file: tests/test_intelligence.py
from importlib import import_module

from fastapi.testclient import TestClient

app = import_module("app.main").app
client = TestClient(app)


def test_buyscore_endpoint() -> None:
    response = client.get("/api/v1/intelligence/buyscore/555088-001")
    assert response.status_code == 200

    payload = response.json()
    assert payload["sku"] == "555088-001"
    assert 35 <= payload["buy_score"] <= 99
    assert len(payload["culture_vector"]) == 15
    assert "market_momentum" in payload["components"]
    assert "partial" in payload["meta"]


def test_correlation_endpoint() -> None:
    response = client.get("/api/v1/intelligence/correlation", params={"period": "1d"})
    assert response.status_code == 200

    payload = response.json()
    assert payload["items"]
    assert isinstance(payload["summary"], str)
    assert payload["meta"]["source"]


def test_intake_csv_and_url() -> None:
    csv_response = client.post(
        "/api/v1/intelligence/intake",
        json={
            "intake_type": "csv",
            "payload": "sku,model\nTEST-A,Model A\nTEST-B,Model B\n",
        },
    )
    assert csv_response.status_code == 200
    csv_payload = csv_response.json()
    assert csv_payload["accepted"] is True
    assert csv_payload["parsed_items"] == 2
    assert len(csv_payload["preview"]) == 2

    url_response = client.post(
        "/api/v1/intelligence/intake",
        json={
            "intake_type": "url",
            "payload": "https://example.com/sneaker/123",
        },
    )
    assert url_response.status_code == 200
    url_payload = url_response.json()
    assert url_payload["accepted"] is True
    assert url_payload["parsed_items"] == 1
    assert url_payload["preview"][0]["sku"].startswith("URL-")