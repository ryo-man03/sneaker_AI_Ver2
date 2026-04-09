from datetime import datetime

from pydantic import BaseModel


class TableCounts(BaseModel):
    sneakers: int
    market_snapshots: int
    stock_snapshots: int
    wishlist_items: int
    closet_items: int
    price_alert_rules: int
    notification_events: int


class SchedulerStatus(BaseModel):
    running: bool
    interval_seconds: int


class IntegrationStatus(BaseModel):
    gemini_configured: bool
    instagram_configured: bool


class HardeningStatus(BaseModel):
    lifespan_mode: str
    security_headers_enabled: bool
    trusted_hosts: list[str]


class MaintenanceStatus(BaseModel):
    key_rotation_days: int
    dependency_audit_days: int
    release_channel: str


class DqmCheck(BaseModel):
    key: str
    ok: bool
    detail: str


class DqmSummary(BaseModel):
    passed: bool
    stale_count: int
    checks: list[DqmCheck]


class AdminOpsData(BaseModel):
    db_counts: TableCounts
    scheduler: SchedulerStatus
    integrations: IntegrationStatus
    hardening: HardeningStatus
    maintenance: MaintenanceStatus
    dqm: DqmSummary


class AdminOpsResponse(BaseModel):
    data: AdminOpsData
    source: str
    updated_at: datetime
    ai_available: bool
    partial: bool
    error_message: str | None = None