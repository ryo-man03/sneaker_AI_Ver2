# file: app/api/routers/portfolio.py
from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.closet import ClosetItem
from app.schemas.core_data import DataMeta
from app.schemas.user_assets import PortfolioHolding, PortfolioResponse

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("", response_model=PortfolioResponse)
async def get_portfolio(session: AsyncSession = Depends(get_session)) -> PortfolioResponse:
    rows = (await session.execute(select(ClosetItem).order_by(ClosetItem.id.asc()))).scalars().all()

    holdings: list[PortfolioHolding] = []
    total_cost = 0.0
    current_value = 0.0

    for row in rows:
        cost = row.avg_buy_price * row.quantity
        value = row.current_price * row.quantity
        pnl = value - cost
        roi_pct = (pnl / cost * 100) if cost > 0 else 0.0

        holdings.append(
            PortfolioHolding(
                id=row.id,
                sku=row.sku,
                model=row.model,
                quantity=row.quantity,
                total_cost=round(cost, 2),
                current_value=round(value, 2),
                unrealized_pnl=round(pnl, 2),
                roi_pct=round(roi_pct, 2),
            )
        )
        total_cost += cost
        current_value += value

    unrealized_pnl = current_value - total_cost
    roi_pct = (unrealized_pnl / total_cost * 100) if total_cost > 0 else 0.0

    return PortfolioResponse(
        total_cost=round(total_cost, 2),
        current_value=round(current_value, 2),
        unrealized_pnl=round(unrealized_pnl, 2),
        roi_pct=round(roi_pct, 2),
        holdings=holdings,
        meta=DataMeta(
            source="seeded-db",
            updated_at=datetime.now(UTC),
            partial=False,
            ai_available=False,
        ),
    )
