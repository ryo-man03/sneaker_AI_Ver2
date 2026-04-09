# file: app/api/routers/instagram.py
from datetime import UTC, datetime

from fastapi import APIRouter, Query

from app.schemas.instagram import InstagramTrendResponse
from app.services.social_trends import fetch_instagram_trends

router = APIRouter(prefix="/instagram", tags=["instagram"])


@router.get("/trends", response_model=InstagramTrendResponse)
async def get_instagram_trends(
    hashtag: str = Query(default="sneakers", min_length=1, max_length=100),
    limit: int = Query(default=10, ge=1, le=30),
) -> InstagramTrendResponse:
    result = await fetch_instagram_trends(hashtag=hashtag, limit=limit)
    return InstagramTrendResponse(
        data=result.data,
        source=result.source,
        updated_at=datetime.now(UTC),
        ai_available=result.ai_available,
        partial=result.partial,
        error_message=result.error_message,
    )
