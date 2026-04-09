# file: app/api/routers/stocks.py
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.stock import StockSnapshot
from app.schemas.core_data import DataMeta, StockRow, StocksResponse

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("", response_model=StocksResponse)
async def get_stocks(
    period: str = Query(default="1d"),
    session: AsyncSession = Depends(get_session),
) -> StocksResponse:
    rows = (await session.execute(select(StockSnapshot).where(StockSnapshot.period == period))).scalars().all()

    items = [
        StockRow(
            ticker=row.ticker,
            company=row.company,
            price=row.price,
            change_pct=row.change_pct,
            direction="up" if row.change_pct >= 0 else "down",
            index_name=row.index_name,
            index_change_pct=row.index_change_pct,
        )
        for row in rows
    ]

    return StocksResponse(
        period=period,
        items=items,
        correlations_summary="NKE 下落時は ADDYY が逆相関、ONON は正相関傾向",
        meta=DataMeta(
            source="seeded-db",
            updated_at=datetime.now(UTC),
            partial=False,
            ai_available=False,
        ),
    )
