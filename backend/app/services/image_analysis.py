# file: app/services/image_analysis.py
from __future__ import annotations

import json
import re
from dataclasses import dataclass

from app.integrations.gemini_client import GeminiClient
from app.schemas.image_analysis import ImageAnalysisData, ImageAnalysisRequest


@dataclass(slots=True)
class ImageAnalysisResult:
    data: ImageAnalysisData
    source: str
    ai_available: bool
    partial: bool
    error_message: str | None


async def analyze_image(request: ImageAnalysisRequest) -> ImageAnalysisResult:
    client = GeminiClient()
    fallback = _build_fallback_data(request)

    if not client.available():
        return ImageAnalysisResult(
            data=fallback,
            source="gemini-fallback",
            ai_available=False,
            partial=True,
            error_message="Gemini API key is not configured",
        )

    try:
        result = await client.analyze_image(
            image_url=request.image_url,
            image_base64=request.image_base64,
            mime_type=request.mime_type,
            hint_text=request.hint_text,
        )
        parsed = _parse_gemini_json(result.text)
        return ImageAnalysisResult(
            data=parsed,
            source=f"gemini:{result.model}",
            ai_available=True,
            partial=False,
            error_message=None,
        )
    except RuntimeError as exc:
        return ImageAnalysisResult(
            data=fallback,
            source="gemini-fallback",
            ai_available=True,
            partial=True,
            error_message=str(exc),
        )


def _build_fallback_data(request: ImageAnalysisRequest) -> ImageAnalysisData:
    sample = f"{request.image_url or ''} {request.hint_text}".lower()
    brand = "UNKNOWN"
    model = "Unknown Sneaker"
    colorway = "Unknown"

    for candidate in ("nike", "adidas", "new balance", "asics"):
        if candidate in sample:
            brand = candidate.upper() if candidate != "new balance" else "NEW BALANCE"

    sku_match = re.search(r"[a-z0-9]{3,}-[a-z0-9]{2,}", sample)
    if sku_match:
        model = f"Candidate {sku_match.group(0).upper()}"

    if "black" in sample:
        colorway = "Black"
    if "red" in sample:
        colorway = "Red"

    notes = ["fallback-estimation", "verify-with-manual-review"]
    is_sneaker = any(token in sample for token in ("sneaker", "nike", "adidas", "jordan", "yeezy"))

    return ImageAnalysisData(
        is_sneaker=is_sneaker,
        brand=brand,
        model=model,
        colorway=colorway,
        material="Unknown",
        notes=notes,
        confidence=0.42 if is_sneaker else 0.25,
    )


def _parse_gemini_json(text: str) -> ImageAnalysisData:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json", "", 1).strip()

    payload = json.loads(cleaned)
    if not isinstance(payload, dict):
        raise RuntimeError("Gemini image response is not JSON object")

    notes_raw = payload.get("notes")
    notes: list[str]
    if isinstance(notes_raw, list):
        notes = [str(item) for item in notes_raw][:10]
    else:
        notes = []

    return ImageAnalysisData(
        is_sneaker=bool(payload.get("is_sneaker", False)),
        brand=str(payload.get("brand") or "UNKNOWN"),
        model=str(payload.get("model") or "Unknown Sneaker"),
        colorway=str(payload.get("colorway") or "Unknown"),
        material=str(payload.get("material") or "Unknown"),
        notes=notes,
        confidence=float(payload.get("confidence") or 0.0),
    )
