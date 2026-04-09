from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.admin_ops import AdminOpsResponse
from app.services.admin_ops import collect_admin_ops

router = APIRouter(prefix="/admin-ops", tags=["admin-ops"])


@router.get("/reliability", response_model=AdminOpsResponse)
async def get_admin_ops_reliability(
    session: AsyncSession = Depends(get_session),
) -> AdminOpsResponse:
    result = await collect_admin_ops(session)
    return AdminOpsResponse(
        data=result.data,
        source=result.source,
        updated_at=datetime.now(UTC),
        ai_available=result.ai_available,
        partial=result.partial,
        error_message=result.error_message,
    )
