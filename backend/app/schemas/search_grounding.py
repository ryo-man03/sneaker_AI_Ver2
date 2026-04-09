# file: app/schemas/search_grounding.py
from datetime import datetime

from pydantic import BaseModel, Field


class SearchGroundingRequest(BaseModel):
    query: str = Field(min_length=1, max_length=300)
    max_citations: int = Field(default=5, ge=1, le=10)


class GroundingCitation(BaseModel):
    title: str
    url: str
    snippet: str


class SearchGroundingData(BaseModel):
    query: str
    answer: str
    citations: list[GroundingCitation]


class SearchGroundingResponse(BaseModel):
    data: SearchGroundingData
    source: str
    updated_at: datetime
    ai_available: bool
    partial: bool
    error_message: str | None = None
