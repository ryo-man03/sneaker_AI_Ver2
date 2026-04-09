from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import settings
from app.models.closet import ClosetItem
from app.models.market import MarketSnapshot
from app.models.notification_event import NotificationEvent
from app.models.price_alert import PriceAlertRule
from app.models.sneaker import Sneaker
from app.models.stock import StockSnapshot
from app.models.wishlist import WishlistItem
from app.schemas.admin_ops import (
    AdminOpsData,
    DqmCheck,
    DqmSummary,
    HardeningStatus,
    IntegrationStatus,
    MaintenanceStatus,
    SchedulerStatus,
    TableCounts,
)
from app.services.alert_scheduler import scheduler_interval_seconds, scheduler_running


@dataclass(slots=True)
class AdminOpsResult:
    data: AdminOpsData
    source: str
    ai_available: bool
    partial: bool
    error_message: str | None


async def collect_admin_ops(session: AsyncSession) -> AdminOpsResult:
    try:
        counts = await _load_counts(session)
        latest_market = await session.scalar(select(func.max(MarketSnapshot.updated_at)))
        latest_stock = await session.scalar(select(func.max(StockSnapshot.updated_at)))
        latest_notification = await session.scalar(select(func.max(NotificationEvent.created_at)))

        dqm = _build_dqm(
            counts=counts,
            latest_market=_as_utc_or_none(latest_market),
            latest_stock=_as_utc_or_none(latest_stock),
            latest_notification=_as_utc_or_none(latest_notification),
        )

        data = AdminOpsData(
            db_counts=counts,
            scheduler=SchedulerStatus(
                running=scheduler_running(),
                interval_seconds=scheduler_interval_seconds(),
            ),
            integrations=IntegrationStatus(
                gemini_configured=bool(settings.gemini_api_key),
                instagram_configured=bool(
                    settings.instagram_access_token and settings.instagram_business_account_id
                ),
            ),
            hardening=HardeningStatus(
                lifespan_mode="enabled",
                security_headers_enabled=settings.security_headers_enabled,
                trusted_hosts=settings.trusted_hosts_list,
            ),
            maintenance=MaintenanceStatus(
                key_rotation_days=settings.maintenance_key_rotation_days,
                dependency_audit_days=settings.maintenance_dependency_audit_days,
                release_channel=settings.maintenance_release_channel,
            ),
            dqm=dqm,
        )
        return AdminOpsResult(
            data=data,
            source="admin-ops",
            ai_available=False,
            partial=False,
            error_message=None,
        )
    except Exception as exc:
        empty = TableCounts(
            sneakers=0,
            market_snapshots=0,
            stock_snapshots=0,
            wishlist_items=0,
            closet_items=0,
            price_alert_rules=0,
            notification_events=0,
        )
        fallback = AdminOpsData(
            db_counts=empty,
            scheduler=SchedulerStatus(
                running=scheduler_running(),
                interval_seconds=scheduler_interval_seconds(),
            ),
            integrations=IntegrationStatus(
                gemini_configured=bool(settings.gemini_api_key),
                instagram_configured=bool(
                    settings.instagram_access_token and settings.instagram_business_account_id
                ),
            ),
            hardening=HardeningStatus(
                lifespan_mode="enabled",
                security_headers_enabled=settings.security_headers_enabled,
                trusted_hosts=settings.trusted_hosts_list,
            ),
            maintenance=MaintenanceStatus(
                key_rotation_days=settings.maintenance_key_rotation_days,
                dependency_audit_days=settings.maintenance_dependency_audit_days,
                release_channel=settings.maintenance_release_channel,
            ),
            dqm=DqmSummary(
                passed=False,
                stale_count=1,
                checks=[DqmCheck(key="admin_ops_fetch", ok=False, detail="fallback")],
            ),
        )
        return AdminOpsResult(
            data=fallback,
            source="admin-ops-fallback",
            ai_available=False,
            partial=True,
            error_message=f"admin ops collection failed ({type(exc).__name__})",
        )


async def _load_counts(session: AsyncSession) -> TableCounts:
    sneakers = int(await _count_rows(session, Sneaker))
    market_snapshots = int(await _count_rows(session, MarketSnapshot))
    stock_snapshots = int(await _count_rows(session, StockSnapshot))
    wishlist_items = int(await _count_rows(session, WishlistItem))
    closet_items = int(await _count_rows(session, ClosetItem))
    price_alert_rules = int(await _count_rows(session, PriceAlertRule))
    notification_events = int(await _count_rows(session, NotificationEvent))
    return TableCounts(
        sneakers=sneakers,
        market_snapshots=market_snapshots,
        stock_snapshots=stock_snapshots,
        wishlist_items=wishlist_items,
        closet_items=closet_items,
        price_alert_rules=price_alert_rules,
        notification_events=notification_events,
    )


async def _count_rows(session: AsyncSession, model: type[object]) -> int:
    value = await session.scalar(select(func.count()).select_from(model))
    return int(value or 0)


def _build_dqm(
    *,
    counts: TableCounts,
    latest_market: datetime | None,
    latest_stock: datetime | None,
    latest_notification: datetime | None,
) -> DqmSummary:
    now = datetime.now(UTC)
    checks: list[DqmCheck] = []

    checks.append(
        DqmCheck(
            key="core_data_seeded",
            ok=counts.sneakers > 0,
            detail=f"sneakers={counts.sneakers}",
        )
    )
    checks.append(
        _freshness_check(
            key="market_freshness",
            latest=latest_market,
            now=now,
            max_age=timedelta(hours=24),
        )
    )
    checks.append(
        _freshness_check(
            key="stocks_freshness",
            latest=latest_stock,
            now=now,
            max_age=timedelta(hours=24),
        )
    )
    checks.append(
        _freshness_check(
            key="notifications_recent",
            latest=latest_notification,
            now=now,
            max_age=timedelta(days=7),
        )
    )

    stale_count = sum(0 if check.ok else 1 for check in checks)
    return DqmSummary(
        passed=stale_count == 0,
        stale_count=stale_count,
        checks=checks,
    )


def _freshness_check(*, key: str, latest: datetime | None, now: datetime, max_age: timedelta) -> DqmCheck:
    if latest is None:
        return DqmCheck(key=key, ok=False, detail="latest=missing")

    age_seconds = int((now - latest).total_seconds())
    ok = age_seconds <= int(max_age.total_seconds())
    return DqmCheck(
        key=key,
        ok=ok,
        detail=f"age_seconds={age_seconds}, max={int(max_age.total_seconds())}",
    )


def _as_utc_or_none(value: object) -> datetime | None:
    if not isinstance(value, datetime):
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
