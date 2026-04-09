# file: app/schemas/intelligence.py
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.core_data import DataMeta

IntakeType = Literal["image", "url", "csv"]


class CultureVectorPoint(BaseModel):
    label: str
    score: float


class CultureVectorResponse(BaseModel):
    sku: str
    model: str
    vector: list[CultureVectorPoint]
    meta: DataMeta


class BuyScoreComponents(BaseModel):
    market_momentum: int
    liquidity: int
    stock_correlation: int
    culture_signal: int
    risk_penalty: int


class BuyScoreResponse(BaseModel):
    sku: str
    model: str
    brand: str
    buy_score: int
    fallback_reason: str | None
    components: BuyScoreComponents
    culture_vector: list[CultureVectorPoint]
    meta: DataMeta


class CorrelationItem(BaseModel):
    ticker: str
    company: str
    correlation: float
    relation: str
    change_pct: float
    index_change_pct: float


class CorrelationResponse(BaseModel):
    period: str
    items: list[CorrelationItem]
    summary: str
    meta: DataMeta


class IntakeRequest(BaseModel):
    intake_type: IntakeType
    payload: str = Field(min_length=1, max_length=200_000)
    file_name: str | None = Field(default=None, max_length=255)


class IntakePreviewItem(BaseModel):
    sku: str
    model: str
    hint: str


class IntakeResponse(BaseModel):
    intake_type: IntakeType
    parsed_items: int
    accepted: bool
    preview: list[IntakePreviewItem]
    warnings: list[str]
    meta: DataMeta