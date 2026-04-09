# file: tests/test_user_assets.py
from importlib import import_module

from fastapi.testclient import TestClient

app = import_module("app.main").app
client = TestClient(app)


def test_wishlist_crud_and_price_alert_rule() -> None:
    create_response = client.post(
        "/api/v1/wishlist",
        json={
            "sku": "TEST-WL-001",
            "model": "Test Wishlist Model",
            "brand": "TEST",
            "target_price": 21000,
            "current_price": 25000,
            "note": "phase4 test",
        },
    )
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]

    list_response = client.get("/api/v1/wishlist")
    assert list_response.status_code == 200
    payload = list_response.json()
    assert any(item["id"] == item_id for item in payload["items"])
    assert payload["meta"]["source"]

    alert_create = client.post(
        "/api/v1/price-alerts",
        json={
            "sku": "TEST-WL-001",
            "rule_type": "price_below",
            "threshold": 20500,
            "active": True,
            "cooldown_minutes": 120,
        },
    )
    assert alert_create.status_code == 201
    rule_id = alert_create.json()["id"]

    alert_update = client.patch(
        f"/api/v1/price-alerts/{rule_id}",
        json={"threshold": 19900, "active": False},
    )
    assert alert_update.status_code == 200
    assert alert_update.json()["threshold"] == 19900
    assert alert_update.json()["active"] is False

    alert_delete = client.delete(f"/api/v1/price-alerts/{rule_id}")
    assert alert_delete.status_code == 204

    delete_response = client.delete(f"/api/v1/wishlist/{item_id}")
    assert delete_response.status_code == 204


def test_closet_crud_and_portfolio_summary() -> None:
    create_response = client.post(
        "/api/v1/closet",
        json={
            "sku": "TEST-CL-001",
            "model": "Test Closet Model",
            "brand": "TEST",
            "quantity": 2,
            "avg_buy_price": 18000,
            "current_price": 21000,
        },
    )
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]

    patch_response = client.patch(
        f"/api/v1/closet/{item_id}",
        json={"quantity": 3, "current_price": 22000},
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["quantity"] == 3

    portfolio_response = client.get("/api/v1/portfolio")
    assert portfolio_response.status_code == 200
    portfolio_payload = portfolio_response.json()
    assert "total_cost" in portfolio_payload
    assert "current_value" in portfolio_payload
    assert isinstance(portfolio_payload["holdings"], list)
    assert portfolio_payload["meta"]["source"]

    delete_response = client.delete(f"/api/v1/closet/{item_id}")
    assert delete_response.status_code == 204
