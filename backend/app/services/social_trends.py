# file: app/services/social_trends.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from app.integrations.instagram_client import InstagramClient
from app.schemas.instagram import InstagramTrendData, InstagramTrendItem


@dataclass(slots=True)
class TrendFetchResult:
    data: InstagramTrendData
    source: str
    ai_available: bool
    partial: bool
    error_message: str | None


async def fetch_instagram_trends(*, hashtag: str, limit: int) -> TrendFetchResult:
    client = InstagramClient()

    if not client.available():
        return TrendFetchResult(
            data=_fallback_data(hashtag=hashtag),
            source="instagram",
            ai_available=False,
            partial=True,
            error_message="Instagram credentials are not configured",
        )

    try:
        rows = await client.fetch_hashtag_trends(hashtag=hashtag, limit=limit)
        items = [_normalize_item(hashtag=hashtag, row=row) for row in rows]
        return TrendFetchResult(
            data=InstagramTrendData(
                query=hashtag,
                total=len(items),
                items=items,
            ),
            source="instagram",
            ai_available=True,
            partial=False,
            error_message=None,
        )
    except RuntimeError as exc:
        return TrendFetchResult(
            data=_fallback_data(hashtag=hashtag),
            source="instagram",
            ai_available=True,
            partial=True,
            error_message=str(exc),
        )


def _normalize_item(*, hashtag: str, row: object) -> InstagramTrendItem:
    from app.integrations.instagram_client import InstagramMedia

    media = row if isinstance(row, InstagramMedia) else InstagramMedia("", "unknown", "", 0, 0, datetime.now(UTC))
    score = float(media.like_count + media.comments_count * 1.8)

    return InstagramTrendItem(
        hashtag=hashtag if hashtag.startswith("#") else f"#{hashtag}",
        caption=media.caption[:300],
        media_type=media.media_type,
        permalink=media.permalink,
        engagement_score=round(score, 2),
        observed_at=media.timestamp,
    )


def _fallback_data(*, hashtag: str) -> InstagramTrendData:
    now = datetime.now(UTC)
    tag = hashtag if hashtag.startswith("#") else f"#{hashtag}"
    return InstagramTrendData(
        query=hashtag,
        total=1,
        items=[
            InstagramTrendItem(
                hashtag=tag,
                caption="fallback trend item",
                media_type="IMAGE",
                permalink="",
                engagement_score=0.0,
                observed_at=now,
            )
        ],
    )
