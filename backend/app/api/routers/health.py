# file: app/api/routers/health.py
from fastapi import APIRouter

from app.core.settings import settings
from app.schemas.health import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
def get_health() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        service=settings.app_name,
        version=settings.app_version,
    )
