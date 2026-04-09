# file: app/api/routers/search.py
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.sneaker import Sneaker
from app.schemas.core_data import DataMeta, SearchResponse, SearchResultItem

router = APIRouter(prefix="/search", tags=["search"])


def _rank_value(query: str, sku: str, model: str, brand: str, note: str) -> float:
    q = query.lower()
    score = 0.0
    if q in sku.lower():
        score += 4.0
    if q in model.lower():
        score += 3.0
    if q in brand.lower():
        score += 2.0
    if q in note.lower():
        score += 1.0
    return score


@router.get("", response_model=SearchResponse)
async def search_sneakers(
    q: str = Query(default="", max_length=100),
    session: AsyncSession = Depends(get_session),
) -> SearchResponse:
    rows = (await session.execute(select(Sneaker))).scalars().all()

    items: list[SearchResultItem] = []
    for row in rows:
        rank = _rank_value(q, row.sku, row.model, row.brand, row.note)
        if q and rank <= 0:
            continue
        items.append(
            SearchResultItem(
                sku=row.sku,
                model=row.model,
                brand=row.brand,
                retail_price=row.retail_price,
                market_price=row.market_price,
                buy_score=row.buy_score,
                liquidity=row.liquidity,
                note=row.note,
                rank=rank if q else float(row.buy_score),
            )
        )

    items.sort(key=lambda item: (item.rank, item.buy_score), reverse=True)

    return SearchResponse(
        query=q,
        total=len(items),
        items=items,
        meta=DataMeta(
            source="seeded-db",
            updated_at=datetime.now(UTC),
            partial=False,
            ai_available=False,
        ),
    )
