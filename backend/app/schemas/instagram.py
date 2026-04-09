# file: app/schemas/instagram.py
from datetime import datetime

from pydantic import BaseModel, Field


class InstagramTrendItem(BaseModel):
    hashtag: str
    caption: str
    media_type: str
    permalink: str
    engagement_score: float
    observed_at: datetime


class InstagramTrendData(BaseModel):
    query: str
    total: int
    items: list[InstagramTrendItem]


class InstagramTrendRequest(BaseModel):
    hashtag: str = Field(min_length=1, max_length=100)
    limit: int = Field(default=10, ge=1, le=30)


class InstagramTrendResponse(BaseModel):
    data: InstagramTrendData
    source: str
    updated_at: datetime
    ai_available: bool
    partial: bool
    error_message: str | None = None
