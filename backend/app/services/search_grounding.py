# file: app/services/search_grounding.py
from __future__ import annotations

import re
from dataclasses import dataclass

from app.integrations.gemini_client import GeminiClient
from app.schemas.search_grounding import GroundingCitation, SearchGroundingData


@dataclass(slots=True)
class SearchGroundingResult:
    data: SearchGroundingData
    source: str
    ai_available: bool
    partial: bool
    error_message: str | None


async def generate_grounded_answer(*, query: str, max_citations: int) -> SearchGroundingResult:
    client = GeminiClient()

    if not client.available():
        return SearchGroundingResult(
            data=_fallback_answer(query=query),
            source="grounding-fallback",
            ai_available=False,
            partial=True,
            error_message="Gemini API key is not configured",
        )

    try:
        result = await client.grounded_answer(query=query, max_citations=max_citations)
        citations = _extract_citations(result.text, max_citations=max_citations)
        return SearchGroundingResult(
            data=SearchGroundingData(
                query=query,
                answer=result.text,
                citations=citations,
            ),
            source=f"grounded-search:{result.model}",
            ai_available=True,
            partial=False,
            error_message=None,
        )
    except RuntimeError as exc:
        return SearchGroundingResult(
            data=_fallback_answer(query=query),
            source="grounding-fallback",
            ai_available=True,
            partial=True,
            error_message=str(exc),
        )


def _extract_citations(text: str, *, max_citations: int) -> list[GroundingCitation]:
    url_pattern = re.compile(r"https?://[^\s)]+")
    urls = url_pattern.findall(text)

    citations: list[GroundingCitation] = []
    for index, url in enumerate(urls[:max_citations], start=1):
        citations.append(
            GroundingCitation(
                title=f"source-{index}",
                url=url,
                snippet="Gemini grounded output",
            )
        )

    if citations:
        return citations

    return [
        GroundingCitation(
            title="no-citation",
            url="",
            snippet="No explicit URL citation was returned by the model",
        )
    ]


def _fallback_answer(*, query: str) -> SearchGroundingData:
    return SearchGroundingData(
        query=query,
        answer=(
            "検索補助AIは現在フォールバック動作です。"
            " query を受け取りましたが、外部grounding未利用のため要手動確認です。"
        ),
        citations=[],
    )
