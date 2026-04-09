# file: app/api/routers/notifications.py
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import settings
from app.db.session import get_session
from app.models.notification_event import NotificationEvent
from app.schemas.alerts_delivery import (
    AlertDispatchResponse,
    NotificationCenterResponse,
    NotificationEventOut,
    SchedulerStatusResponse,
)
from app.schemas.core_data import DataMeta
from app.services.alert_scheduler import (
    evaluate_alert_rules,
    scheduler_interval_seconds,
    scheduler_running,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=NotificationCenterResponse)
async def list_notifications(
    limit: int = Query(default=settings.notification_center_default_limit, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
) -> NotificationCenterResponse:
    rows = (
        await session.execute(
            select(NotificationEvent).order_by(NotificationEvent.created_at.desc()).limit(limit)
        )
    ).scalars().all()

    return NotificationCenterResponse(
        items=[NotificationEventOut.model_validate(row, from_attributes=True) for row in rows],
        meta=DataMeta(
            source="scheduler",
            updated_at=datetime.now(UTC),
            partial=False,
            ai_available=False,
        ),
    )


@router.post("/run", response_model=AlertDispatchResponse)
async def run_notification_dispatch(session: AsyncSession = Depends(get_session)) -> AlertDispatchResponse:
    stats = await evaluate_alert_rules(session)
    return AlertDispatchResponse(
        status="ok",
        evaluated=stats.evaluated,
        triggered=stats.triggered,
        duplicates=stats.duplicates,
        cooldown_skipped=stats.cooldown_skipped,
        missing_market=stats.missing_market,
        scheduler_running=scheduler_running(),
        interval_seconds=scheduler_interval_seconds(),
        meta=DataMeta(
            source="scheduler",
            updated_at=datetime.now(UTC),
            partial=False,
            ai_available=False,
        ),
    )


@router.get("/scheduler", response_model=SchedulerStatusResponse)
async def get_scheduler_status() -> SchedulerStatusResponse:
    return SchedulerStatusResponse(
        running=scheduler_running(),
        interval_seconds=scheduler_interval_seconds(),
        meta=DataMeta(
            source="scheduler",
            updated_at=datetime.now(UTC),
            partial=False,
            ai_available=False,
        ),
    )
