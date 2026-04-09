# file: app/schemas/image_analysis.py
from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class ImageAnalysisRequest(BaseModel):
    image_url: str | None = Field(default=None, max_length=2000)
    image_base64: str | None = Field(default=None, max_length=2_000_000)
    mime_type: str = Field(default="image/jpeg", max_length=100)
    hint_text: str = Field(default="", max_length=500)

    @model_validator(mode="after")
    def validate_image_source(self) -> "ImageAnalysisRequest":
        if not self.image_url and not self.image_base64:
            raise ValueError("image_url or image_base64 is required")
        return self


class ImageAnalysisData(BaseModel):
    is_sneaker: bool
    brand: str
    model: str
    colorway: str
    material: str
    notes: list[str]
    confidence: float


class ImageAnalysisResponse(BaseModel):
    data: ImageAnalysisData
    source: str
    updated_at: datetime
    ai_available: bool
    partial: bool
    error_message: str | None = None
