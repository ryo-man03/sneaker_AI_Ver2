# file: app/models/market.py
from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MarketSnapshot(Base):
    __tablename__ = "market_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sku: Mapped[str] = mapped_column(String(64), index=True)
    period: Mapped[str] = mapped_column(String(16), index=True)
    ask_price: Mapped[float] = mapped_column(Float)
    bid_price: Mapped[float] = mapped_column(Float)
    last_sale: Mapped[float] = mapped_column(Float)
    liquidity: Mapped[str] = mapped_column(String(16))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
