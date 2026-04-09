# file: app/api/routers/search_grounding.py
from datetime import UTC, datetime

from fastapi import APIRouter

from app.schemas.search_grounding import (
    SearchGroundingRequest,
    SearchGroundingResponse,
)
from app.services.search_grounding import generate_grounded_answer

router = APIRouter(prefix="/search-grounding", tags=["search-grounding"])


@router.post("/answer", response_model=SearchGroundingResponse)
async def post_grounded_answer(request: SearchGroundingRequest) -> SearchGroundingResponse:
    result = await generate_grounded_answer(
        query=request.query,
        max_citations=request.max_citations,
    )
    return SearchGroundingResponse(
        data=result.data,
        source=result.source,
        updated_at=datetime.now(UTC),
        ai_available=result.ai_available,
        partial=result.partial,
        error_message=result.error_message,
    )
