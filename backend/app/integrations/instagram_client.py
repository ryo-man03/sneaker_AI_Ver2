# file: app/integrations/instagram_client.py
from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import cast
from urllib import error, parse, request

from app.core.settings import settings


@dataclass(slots=True)
class InstagramMedia:
    caption: str
    media_type: str
    permalink: str
    like_count: int
    comments_count: int
    timestamp: datetime


class InstagramClient:
    def __init__(self) -> None:
        self._token = settings.instagram_access_token
        self._account_id = settings.instagram_business_account_id
        self._api_version = settings.instagram_api_version
        self._timeout = settings.instagram_timeout_seconds

    def available(self) -> bool:
        return bool(self._token and self._account_id)

    async def fetch_hashtag_trends(self, *, hashtag: str, limit: int) -> list[InstagramMedia]:
        if not self.available():
            raise RuntimeError("Instagram credentials are not configured")

        clean_tag = hashtag.lstrip("#").strip()
        if not clean_tag:
            raise RuntimeError("hashtag is empty")

        hashtag_id = await self._search_hashtag_id(clean_tag)
        if not hashtag_id:
            raise RuntimeError("Instagram hashtag id not found")

        payload = await self._get_json(
            path=f"/{hashtag_id}/recent_media",
            params={
                "user_id": self._account_id,
                "fields": "id,caption,like_count,comments_count,media_type,timestamp,permalink",
                "limit": str(limit),
            },
        )

        rows = payload.get("data")
        if not isinstance(rows, list):
            return []

        media: list[InstagramMedia] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            timestamp = _parse_datetime(row.get("timestamp"))
            media.append(
                InstagramMedia(
                    caption=str(row.get("caption") or ""),
                    media_type=str(row.get("media_type") or "unknown"),
                    permalink=str(row.get("permalink") or ""),
                    like_count=int(row.get("like_count") or 0),
                    comments_count=int(row.get("comments_count") or 0),
                    timestamp=timestamp,
                )
            )
        return media

    async def _search_hashtag_id(self, hashtag: str) -> str:
        payload = await self._get_json(
            path="/ig_hashtag_search",
            params={
                "user_id": self._account_id,
                "q": hashtag,
            },
        )
        rows = payload.get("data")
        if not isinstance(rows, list) or not rows:
            return ""

        first = rows[0]
        if not isinstance(first, dict):
            return ""
        hashtag_id = first.get("id")
        return str(hashtag_id) if hashtag_id else ""

    async def _get_json(self, *, path: str, params: dict[str, str]) -> dict[str, object]:
        query_params = {**params, "access_token": self._token}
        query = parse.urlencode(query_params)
        url = f"https://graph.facebook.com/{self._api_version}{path}?{query}"
        req = request.Request(url=url, method="GET")

        try:
            raw = await asyncio.to_thread(self._open_request, req)
        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError(f"Instagram request failed ({type(exc).__name__})") from exc

        if not isinstance(raw, dict):
            raise RuntimeError("Instagram response shape is invalid")
        return raw

    def _open_request(self, req: request.Request) -> dict[str, object]:
        try:
            with request.urlopen(req, timeout=self._timeout) as response:
                body = response.read().decode("utf-8")
        except error.HTTPError as exc:
            raise RuntimeError(f"Instagram HTTP {exc.code}") from exc
        except error.URLError as exc:
            raise RuntimeError(f"Instagram network error ({exc.reason})") from exc

        try:
            payload = json.loads(body)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Instagram response parse error") from exc

        if not isinstance(payload, dict):
            raise RuntimeError("Instagram response is not an object")

        if "error" in payload:
            raise RuntimeError("Instagram API returned an error")
        return cast(dict[str, object], payload)


def _parse_datetime(raw: object) -> datetime:
    if not isinstance(raw, str) or not raw:
        return datetime.now(UTC)
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return datetime.now(UTC)
