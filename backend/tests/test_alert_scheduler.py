# file: tests/test_alert_scheduler.py
import asyncio
from datetime import UTC, datetime, timedelta
from importlib import import_module

from fastapi.testclient import TestClient

app = import_module("app.main").app
SessionLocal = import_module("app.db.session").SessionLocal
MarketSnapshot = import_module("app.models.market").MarketSnapshot
PriceAlertRule = import_module("app.models.price_alert").PriceAlertRule
client = TestClient(app)


async def _rewind_last_triggered(rule_id: int, minutes_ago: int) -> None:
    async with SessionLocal() as session:
        row = await session.get(PriceAlertRule, rule_id)
        if row is None:
            return
        row.last_triggered_at = datetime.now(UTC) - timedelta(minutes=minutes_ago)
        await session.commit()


async def _insert_market_snapshot(sku: str, last_sale: float) -> None:
    async with SessionLocal() as session:
        session.add(
            MarketSnapshot(
                sku=sku,
                period="1d",
                ask_price=last_sale + 300,
                bid_price=max(1.0, last_sale - 300),
                last_sale=last_sale,
                liquidity="中",
                updated_at=datetime.now(UTC),
            )
        )
        await session.commit()


def test_scheduler_status_and_notification_dedupe_flow() -> None:
    suffix = datetime.now(UTC).strftime("%H%M%S%f")
    sku = f"PH6-{suffix}"
    asyncio.run(_insert_market_snapshot(sku=sku, last_sale=42000))

    scheduler_response = client.get("/api/v1/notifications/scheduler")
    assert scheduler_response.status_code == 200
    scheduler_payload = scheduler_response.json()
    assert "running" in scheduler_payload
    assert scheduler_payload["interval_seconds"] >= 1

    create_rule = client.post(
        "/api/v1/price-alerts",
        json={
            "sku": sku,
            "rule_type": "price_below",
            "threshold": 50000,
            "active": True,
            "cooldown_minutes": 1,
        },
    )
    assert create_rule.status_code == 201
    rule_id = create_rule.json()["id"]

    first_run = client.post("/api/v1/notifications/run")
    assert first_run.status_code == 200
    first_payload = first_run.json()
    assert first_payload["status"] == "ok"
    assert first_payload["triggered"] >= 1

    asyncio.run(_rewind_last_triggered(rule_id, minutes_ago=3))

    second_run = client.post("/api/v1/notifications/run")
    assert second_run.status_code == 200
    second_payload = second_run.json()
    assert second_payload["duplicates"] >= 1

    list_response = client.get("/api/v1/notifications", params={"limit": 20})
    assert list_response.status_code == 200
    list_payload = list_response.json()
    assert isinstance(list_payload["items"], list)
    assert any(item["rule_id"] == rule_id for item in list_payload["items"])
    assert list_payload["meta"]["source"] == "scheduler"

    delete_rule = client.delete(f"/api/v1/price-alerts/{rule_id}")
    assert delete_rule.status_code == 204
