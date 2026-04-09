# file: app/schemas/alerts_delivery.py
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.core_data import DataMeta


class NotificationEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rule_id: int
    sku: str
    rule_type: str
    threshold: float
    trigger_price: float
    dedupe_key: str
    channel: str
    status: str
    message: str
    created_at: datetime


class NotificationCenterResponse(BaseModel):
    items: list[NotificationEventOut]
    meta: DataMeta


class AlertDispatchResponse(BaseModel):
    status: str
    evaluated: int
    triggered: int
    duplicates: int
    cooldown_skipped: int
    missing_market: int
    scheduler_running: bool
    interval_seconds: int
    meta: DataMeta


class SchedulerStatusResponse(BaseModel):
    running: bool
    interval_seconds: int
    meta: DataMeta
