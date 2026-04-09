# file: app/api/routers/closet.py
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.closet import ClosetItem
from app.schemas.core_data import DataMeta
from app.schemas.user_assets import ClosetCreate, ClosetItemOut, ClosetListResponse, ClosetUpdate

router = APIRouter(prefix="/closet", tags=["closet"])


@router.get("", response_model=ClosetListResponse)
async def list_closet(session: AsyncSession = Depends(get_session)) -> ClosetListResponse:
    rows = (await session.execute(select(ClosetItem).order_by(ClosetItem.acquired_at.desc()))).scalars().all()
    items = [ClosetItemOut.model_validate(row, from_attributes=True) for row in rows]
    return ClosetListResponse(
        items=items,
        meta=DataMeta(
            source="seeded-db",
            updated_at=datetime.now(UTC),
            partial=False,
            ai_available=False,
        ),
    )


@router.post("", response_model=ClosetItemOut, status_code=status.HTTP_201_CREATED)
async def create_closet_item(
    payload: ClosetCreate,
    session: AsyncSession = Depends(get_session),
) -> ClosetItemOut:
    row = ClosetItem(**payload.model_dump())
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return ClosetItemOut.model_validate(row, from_attributes=True)


@router.patch("/{item_id}", response_model=ClosetItemOut)
async def update_closet_item(
    item_id: int,
    payload: ClosetUpdate,
    session: AsyncSession = Depends(get_session),
) -> ClosetItemOut:
    row = await session.get(ClosetItem, item_id)
    if row is None:
        raise HTTPException(status_code=404, detail="closet item not found")

    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(row, key, value)

    await session.commit()
    await session.refresh(row)
    return ClosetItemOut.model_validate(row, from_attributes=True)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_closet_item(item_id: int, session: AsyncSession = Depends(get_session)) -> Response:
    row = await session.get(ClosetItem, item_id)
    if row is None:
        raise HTTPException(status_code=404, detail="closet item not found")

    await session.delete(row)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
