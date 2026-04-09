# file: app/api/routers/wishlist.py
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.wishlist import WishlistItem
from app.schemas.core_data import DataMeta
from app.schemas.user_assets import WishlistCreate, WishlistItemOut, WishlistListResponse

router = APIRouter(prefix="/wishlist", tags=["wishlist"])


@router.get("", response_model=WishlistListResponse)
async def list_wishlist(session: AsyncSession = Depends(get_session)) -> WishlistListResponse:
    rows = (await session.execute(select(WishlistItem).order_by(WishlistItem.created_at.desc()))).scalars().all()
    items = [WishlistItemOut.model_validate(row, from_attributes=True) for row in rows]
    return WishlistListResponse(
        items=items,
        meta=DataMeta(
            source="seeded-db",
            updated_at=datetime.now(UTC),
            partial=False,
            ai_available=False,
        ),
    )


@router.post("", response_model=WishlistItemOut, status_code=status.HTTP_201_CREATED)
async def create_wishlist_item(
    payload: WishlistCreate,
    session: AsyncSession = Depends(get_session),
) -> WishlistItemOut:
    row = WishlistItem(**payload.model_dump())
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return WishlistItemOut.model_validate(row, from_attributes=True)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_wishlist_item(item_id: int, session: AsyncSession = Depends(get_session)) -> Response:
    row = await session.get(WishlistItem, item_id)
    if row is None:
        raise HTTPException(status_code=404, detail="wishlist item not found")

    await session.delete(row)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
