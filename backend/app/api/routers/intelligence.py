# file: app/api/routers/intelligence.py
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.market import MarketSnapshot
from app.models.sneaker import Sneaker
from app.models.stock import StockSnapshot
from app.schemas.core_data import DataMeta
from app.schemas.intelligence import (
    BuyScoreComponents,
    BuyScoreResponse,
    CorrelationItem,
    CorrelationResponse,
    CultureVectorPoint,
    CultureVectorResponse,
    IntakePreviewItem,
    IntakeRequest,
    IntakeResponse,
)
from app.services.intelligence import (
    ai_available,
    build_culture_vector,
    build_stock_correlation,
    calculate_buy_score,
    parse_intake_payload,
)

router = APIRouter(prefix="/intelligence", tags=["intelligence"])


def _build_meta(source: str, partial: bool, ai_enabled: bool) -> DataMeta:
    return DataMeta(
        source=source,
        updated_at=datetime.now(UTC),
        partial=partial,
        ai_available=ai_enabled,
    )


@router.get("/buyscore/{sku}", response_model=BuyScoreResponse)
async def get_buy_score(
    sku: str,
    period: str = Query(default="1d"),
    session: AsyncSession = Depends(get_session),
) -> BuyScoreResponse:
    sneaker = await session.scalar(select(Sneaker).where(Sneaker.sku == sku))
    if sneaker is None:
        raise HTTPException(status_code=404, detail="Sneaker not found")

    market = await session.scalar(
        select(MarketSnapshot)
        .where(MarketSnapshot.sku == sku, MarketSnapshot.period == period)
        .order_by(MarketSnapshot.updated_at.desc())
    )
    stocks = list(
        (await session.execute(select(StockSnapshot).where(StockSnapshot.period == period))).scalars().all()
    )

    score, parts, fallback_reason = calculate_buy_score(sneaker, market, stocks)
    vector = [CultureVectorPoint(label=label, score=value) for label, value in build_culture_vector(sneaker)]
    ai_enabled = ai_available()

    return BuyScoreResponse(
        sku=sneaker.sku,
        model=sneaker.model,
        brand=sneaker.brand,
        buy_score=score,
        fallback_reason=fallback_reason,
        components=BuyScoreComponents(**parts),
        culture_vector=vector,
        meta=_build_meta(
            source="intelligence-pipeline" if ai_enabled else "intelligence-fallback",
            partial=not ai_enabled,
            ai_enabled=ai_enabled,
        ),
    )


@router.get("/culture-vector/{sku}", response_model=CultureVectorResponse)
async def get_culture_vector(
    sku: str,
    session: AsyncSession = Depends(get_session),
) -> CultureVectorResponse:
    sneaker = await session.scalar(select(Sneaker).where(Sneaker.sku == sku))
    if sneaker is None:
        raise HTTPException(status_code=404, detail="Sneaker not found")

    vector = [CultureVectorPoint(label=label, score=value) for label, value in build_culture_vector(sneaker)]
    ai_enabled = ai_available()
    return CultureVectorResponse(
        sku=sneaker.sku,
        model=sneaker.model,
        vector=vector,
        meta=_build_meta(
            source="culture-engine",
            partial=not ai_enabled,
            ai_enabled=ai_enabled,
        ),
    )


@router.get("/correlation", response_model=CorrelationResponse)
async def get_stock_correlation(
    period: str = Query(default="1d"),
    session: AsyncSession = Depends(get_session),
) -> CorrelationResponse:
    rows = list(
        (await session.execute(select(StockSnapshot).where(StockSnapshot.period == period))).scalars().all()
    )
    points, summary = build_stock_correlation(rows)
    ai_enabled = ai_available()

    return CorrelationResponse(
        period=period,
        items=[CorrelationItem(**point) for point in points],
        summary=summary,
        meta=_build_meta(
            source="correlation-engine",
            partial=not ai_enabled,
            ai_enabled=ai_enabled,
        ),
    )


@router.post("/intake", response_model=IntakeResponse)
async def post_intake(request: IntakeRequest) -> IntakeResponse:
    parsed_items, preview, warnings = parse_intake_payload(request.intake_type, request.payload)
    ai_enabled = ai_available()
    if not ai_enabled:
        warnings.append("AI unavailable: fallback intake parser applied")

    return IntakeResponse(
        intake_type=request.intake_type,
        parsed_items=parsed_items,
        accepted=parsed_items > 0,
        preview=[IntakePreviewItem(**item) for item in preview],
        warnings=warnings,
        meta=_build_meta(
            source="intake-engine" if ai_enabled else "intake-fallback",
            partial=not ai_enabled,
            ai_enabled=ai_enabled,
        ),
    )