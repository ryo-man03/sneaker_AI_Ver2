# file: app/services/alert_scheduler.py
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from importlib import import_module
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import settings
from app.db.session import SessionLocal
from app.models.market import MarketSnapshot
from app.models.notification_event import NotificationEvent
from app.models.price_alert import PriceAlertRule

AsyncIOScheduler = import_module("apscheduler.schedulers.asyncio").AsyncIOScheduler
IntervalTrigger = import_module("apscheduler.triggers.interval").IntervalTrigger


@dataclass(slots=True)
class AlertDispatchStats:
    evaluated: int
    triggered: int
    duplicates: int
    cooldown_skipped: int
    missing_market: int


_scheduler: Any = None
_scheduler_lock = asyncio.Lock()


async def evaluate_alert_rules(session: AsyncSession) -> AlertDispatchStats:
    now = datetime.now(UTC)
    rules = (
        await session.execute(
            select(PriceAlertRule).where(PriceAlertRule.active.is_(True)).order_by(PriceAlertRule.id.asc())
        )
    ).scalars().all()

    triggered = 0
    duplicates = 0
    cooldown_skipped = 0
    missing_market = 0

    for rule in rules:
        latest_market = (
            await session.execute(
                select(MarketSnapshot)
                .where(MarketSnapshot.sku == rule.sku)
                .order_by(MarketSnapshot.updated_at.desc())
            )
        ).scalars().first()

        if latest_market is None:
            missing_market += 1
            continue

        if not _match_condition(rule.rule_type, latest_market.last_sale, rule.threshold):
            continue

        if _is_cooldown(rule, now):
            cooldown_skipped += 1
            continue

        dedupe_key = _build_dedupe_key(rule.id, latest_market.last_sale, latest_market.updated_at)
        duplicate_id = await session.scalar(
            select(NotificationEvent.id).where(NotificationEvent.dedupe_key == dedupe_key)
        )
        if duplicate_id is not None:
            duplicates += 1
            continue

        session.add(
            NotificationEvent(
                rule_id=rule.id,
                sku=rule.sku,
                rule_type=rule.rule_type,
                threshold=rule.threshold,
                trigger_price=latest_market.last_sale,
                dedupe_key=dedupe_key,
                channel="in_app",
                status="sent",
                message=(
                    f"{rule.sku}: {rule.rule_type} threshold={rule.threshold:.0f}, "
                    f"trigger={latest_market.last_sale:.0f}"
                ),
            )
        )
        rule.last_triggered_at = now
        triggered += 1

    await session.commit()
    return AlertDispatchStats(
        evaluated=len(rules),
        triggered=triggered,
        duplicates=duplicates,
        cooldown_skipped=cooldown_skipped,
        missing_market=missing_market,
    )


async def run_dispatch_cycle() -> AlertDispatchStats:
    async with SessionLocal() as session:
        return await evaluate_alert_rules(session)


async def scheduler_job() -> None:
    await run_dispatch_cycle()


async def start_alert_scheduler() -> None:
    global _scheduler
    if not settings.alert_scheduler_enabled:
        return

    async with _scheduler_lock:
        if _scheduler is not None and _scheduler.running:
            return

        scheduler = AsyncIOScheduler(timezone="UTC")
        scheduler.add_job(
            scheduler_job,
            trigger=IntervalTrigger(seconds=settings.alert_scheduler_interval_seconds),
            id="price-alert-dispatch",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
            misfire_grace_time=settings.alert_scheduler_interval_seconds,
        )
        scheduler.start()
        _scheduler = scheduler


async def stop_alert_scheduler() -> None:
    global _scheduler
    async with _scheduler_lock:
        if _scheduler is None:
            return
        _scheduler.shutdown(wait=False)
        _scheduler = None


def scheduler_running() -> bool:
    return _scheduler.running if _scheduler is not None else False


def scheduler_interval_seconds() -> int:
    return settings.alert_scheduler_interval_seconds


def _match_condition(rule_type: str, trigger_price: float, threshold: float) -> bool:
    if rule_type == "price_above":
        return trigger_price >= threshold
    return trigger_price <= threshold


def _is_cooldown(rule: PriceAlertRule, now: datetime) -> bool:
    if rule.last_triggered_at is None:
        return False
    last_triggered_at = _as_utc(rule.last_triggered_at)
    cool_until = last_triggered_at + timedelta(minutes=rule.cooldown_minutes)
    return now < cool_until


def _build_dedupe_key(rule_id: int, trigger_price: float, updated_at: datetime) -> str:
    return f"{rule_id}:{_as_utc(updated_at).isoformat()}:{trigger_price:.2f}"


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
