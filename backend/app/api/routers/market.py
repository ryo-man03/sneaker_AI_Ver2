# file: app/api/routers/market.py
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.market import MarketSnapshot
from app.schemas.core_data import DataMeta, MarketResponse, MarketRow

router = APIRouter(prefix="/market", tags=["market"])


@router.get("", response_model=MarketResponse)
async def get_market(
    period: str = Query(default="1d"),
    session: AsyncSession = Depends(get_session),
) -> MarketResponse:
    rows = (
        await session.execute(select(MarketSnapshot).where(MarketSnapshot.period == period))
    ).scalars().all()

    items: list[MarketRow] = []
    for row in rows:
        spread = ((row.ask_price - row.bid_price) / row.bid_price * 100) if row.bid_price else 0.0
        items.append(
            MarketRow(
                sku=row.sku,
                ask_price=row.ask_price,
                bid_price=row.bid_price,
                spread_pct=round(spread, 2),
                last_sale=row.last_sale,
                liquidity=row.liquidity,
            )
        )

    return MarketResponse(
        period=period,
        items=items,
        meta=DataMeta(
            source="seeded-db",
            updated_at=datetime.now(UTC),
            partial=False,
            ai_available=False,
        ),
    )
