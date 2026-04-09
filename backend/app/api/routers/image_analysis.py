# file: app/api/routers/image_analysis.py
from datetime import UTC, datetime

from fastapi import APIRouter

from app.schemas.image_analysis import ImageAnalysisRequest, ImageAnalysisResponse
from app.services.image_analysis import analyze_image

router = APIRouter(prefix="/image-analysis", tags=["image-analysis"])


@router.post("/analyze", response_model=ImageAnalysisResponse)
async def post_image_analysis(request: ImageAnalysisRequest) -> ImageAnalysisResponse:
    result = await analyze_image(request)
    return ImageAnalysisResponse(
        data=result.data,
        source=result.source,
        updated_at=datetime.now(UTC),
        ai_available=result.ai_available,
        partial=result.partial,
        error_message=result.error_message,
    )
