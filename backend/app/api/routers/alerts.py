# file: app/api/routers/alerts.py
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.price_alert import PriceAlertRule
from app.schemas.core_data import DataMeta
from app.schemas.user_assets import (
    PriceAlertRuleCreate,
    PriceAlertRuleListResponse,
    PriceAlertRuleOut,
    PriceAlertRuleUpdate,
)

router = APIRouter(prefix="/price-alerts", tags=["price-alerts"])


@router.get("", response_model=PriceAlertRuleListResponse)
async def list_price_alert_rules(session: AsyncSession = Depends(get_session)) -> PriceAlertRuleListResponse:
    rows = (await session.execute(select(PriceAlertRule).order_by(PriceAlertRule.created_at.desc()))).scalars().all()
    items = [PriceAlertRuleOut.model_validate(row, from_attributes=True) for row in rows]
    return PriceAlertRuleListResponse(
        items=items,
        meta=DataMeta(
            source="seeded-db",
            updated_at=datetime.now(UTC),
            partial=False,
            ai_available=False,
        ),
    )


@router.post("", response_model=PriceAlertRuleOut, status_code=status.HTTP_201_CREATED)
async def create_price_alert_rule(
    payload: PriceAlertRuleCreate,
    session: AsyncSession = Depends(get_session),
) -> PriceAlertRuleOut:
    row = PriceAlertRule(**payload.model_dump())
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return PriceAlertRuleOut.model_validate(row, from_attributes=True)


@router.patch("/{rule_id}", response_model=PriceAlertRuleOut)
async def update_price_alert_rule(
    rule_id: int,
    payload: PriceAlertRuleUpdate,
    session: AsyncSession = Depends(get_session),
) -> PriceAlertRuleOut:
    row = await session.get(PriceAlertRule, rule_id)
    if row is None:
        raise HTTPException(status_code=404, detail="price alert rule not found")

    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(row, key, value)

    await session.commit()
    await session.refresh(row)
    return PriceAlertRuleOut.model_validate(row, from_attributes=True)


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_price_alert_rule(rule_id: int, session: AsyncSession = Depends(get_session)) -> Response:
    row = await session.get(PriceAlertRule, rule_id)
    if row is None:
        raise HTTPException(status_code=404, detail="price alert rule not found")

    await session.delete(row)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
