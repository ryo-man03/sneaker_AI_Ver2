# file: app/api/routers/sneakers.py
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.market import MarketSnapshot
from app.models.sneaker import Sneaker
from app.schemas.core_data import DataMeta, PricePoint, SneakerDetailResponse, SneakerItem, SneakerListResponse

router = APIRouter(prefix="/sneakers", tags=["sneakers"])


@router.get("", response_model=SneakerListResponse)
async def list_sneakers(session: AsyncSession = Depends(get_session)) -> SneakerListResponse:
    result = await session.execute(select(Sneaker).order_by(Sneaker.buy_score.desc()))
    sneakers = [SneakerItem.model_validate(row, from_attributes=True) for row in result.scalars().all()]

    return SneakerListResponse(
        items=sneakers,
        meta=DataMeta(
            source="seeded-db",
            updated_at=datetime.now(UTC),
            partial=False,
            ai_available=False,
        ),
    )


@router.get("/{sku}", response_model=SneakerDetailResponse)
async def get_sneaker_detail(sku: str, session: AsyncSession = Depends(get_session)) -> SneakerDetailResponse:
    sneaker_row = await session.scalar(select(Sneaker).where(Sneaker.sku == sku))
    if sneaker_row is None:
        raise HTTPException(status_code=404, detail="Sneaker not found")

    history_rows = await session.execute(
        select(MarketSnapshot)
        .where(MarketSnapshot.sku == sku)
        .order_by(MarketSnapshot.updated_at.desc())
        .limit(12)
    )
    history = [
        PricePoint(updated_at=row.updated_at, last_sale=row.last_sale)
        for row in history_rows.scalars().all()
    ]

    return SneakerDetailResponse(
        item=SneakerItem.model_validate(sneaker_row, from_attributes=True),
        market_history=history,
        meta=DataMeta(
            source="seeded-db",
            updated_at=datetime.now(UTC),
            partial=False,
            ai_available=False,
        ),
    )
