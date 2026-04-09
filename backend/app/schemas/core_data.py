# file: app/schemas/core_data.py
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DataMeta(BaseModel):
    source: str
    updated_at: datetime
    partial: bool
    ai_available: bool


class SneakerItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sku: str
    model: str
    brand: str
    retail_price: float
    market_price: float
    buy_score: int
    liquidity: str
    note: str


class PricePoint(BaseModel):
    updated_at: datetime
    last_sale: float


class SneakerListResponse(BaseModel):
    items: list[SneakerItem]
    meta: DataMeta


class SneakerDetailResponse(BaseModel):
    item: SneakerItem
    market_history: list[PricePoint]
    meta: DataMeta


class SearchResultItem(SneakerItem):
    rank: float


class SearchResponse(BaseModel):
    query: str
    total: int
    items: list[SearchResultItem]
    meta: DataMeta


class MarketRow(BaseModel):
    sku: str
    ask_price: float
    bid_price: float
    spread_pct: float
    last_sale: float
    liquidity: str


class MarketResponse(BaseModel):
    period: str
    items: list[MarketRow]
    meta: DataMeta


class StockRow(BaseModel):
    ticker: str
    company: str
    price: float
    change_pct: float
    direction: str
    index_name: str
    index_change_pct: float


class StocksResponse(BaseModel):
    period: str
    items: list[StockRow]
    correlations_summary: str
    meta: DataMeta
