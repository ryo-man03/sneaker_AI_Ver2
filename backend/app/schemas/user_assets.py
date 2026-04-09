# file: app/schemas/user_assets.py
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.core_data import DataMeta


class WishlistItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    model: str
    brand: str
    target_price: float
    current_price: float
    note: str
    created_at: datetime


class WishlistCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    model: str = Field(min_length=1, max_length=255)
    brand: str = Field(min_length=1, max_length=128)
    target_price: float = Field(gt=0)
    current_price: float = Field(gt=0)
    note: str = Field(default="", max_length=255)


class WishlistListResponse(BaseModel):
    items: list[WishlistItemOut]
    meta: DataMeta


class ClosetItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    model: str
    brand: str
    quantity: int
    avg_buy_price: float
    current_price: float
    acquired_at: datetime


class ClosetCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    model: str = Field(min_length=1, max_length=255)
    brand: str = Field(min_length=1, max_length=128)
    quantity: int = Field(default=1, ge=1)
    avg_buy_price: float = Field(gt=0)
    current_price: float = Field(gt=0)


class ClosetUpdate(BaseModel):
    quantity: int | None = Field(default=None, ge=1)
    avg_buy_price: float | None = Field(default=None, gt=0)
    current_price: float | None = Field(default=None, gt=0)


class ClosetListResponse(BaseModel):
    items: list[ClosetItemOut]
    meta: DataMeta


class PortfolioHolding(BaseModel):
    id: int
    sku: str
    model: str
    quantity: int
    total_cost: float
    current_value: float
    unrealized_pnl: float
    roi_pct: float


class PortfolioResponse(BaseModel):
    total_cost: float
    current_value: float
    unrealized_pnl: float
    roi_pct: float
    holdings: list[PortfolioHolding]
    meta: DataMeta


class PriceAlertRuleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    rule_type: str
    threshold: float
    active: bool
    cooldown_minutes: int
    last_triggered_at: datetime | None
    created_at: datetime


class PriceAlertRuleCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    rule_type: str = Field(default="price_below", max_length=32)
    threshold: float = Field(gt=0)
    active: bool = True
    cooldown_minutes: int = Field(default=180, ge=1, le=1440)


class PriceAlertRuleUpdate(BaseModel):
    threshold: float | None = Field(default=None, gt=0)
    active: bool | None = None
    cooldown_minutes: int | None = Field(default=None, ge=1, le=1440)


class PriceAlertRuleListResponse(BaseModel):
    items: list[PriceAlertRuleOut]
    meta: DataMeta
