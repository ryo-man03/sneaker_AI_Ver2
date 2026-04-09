# file: app/integrations/gemini_client.py
from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any, cast
from urllib import error, request

from app.core.settings import settings


@dataclass(slots=True)
class GeminiCallResult:
    text: str
    model: str


class GeminiClient:
    def __init__(self) -> None:
        self._api_key = settings.gemini_api_key or settings.resolved_google_api_key
        self._timeout = settings.gemini_timeout_seconds
        self._default_model = settings.gemini_default_model
        self._fallback_model = settings.gemini_fallback_model

    def available(self) -> bool:
        return bool(self._api_key)

    async def analyze_image(
        self,
        *,
        image_url: str | None,
        image_base64: str | None,
        mime_type: str,
        hint_text: str,
    ) -> GeminiCallResult:
        prompt = (
            "You are a sneaker image analyzer. "
            "Return strict JSON with fields: is_sneaker(bool), brand(str), model(str), "
            "colorway(str), material(str), notes(list[str]), confidence(float 0-1). "
            "If uncertain, keep confidence low and add notes."
        )
        user_description = {
            "image_url": image_url or "",
            "image_base64_present": bool(image_base64),
            "mime_type": mime_type,
            "hint_text": hint_text,
        }
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt},
                        {"text": json.dumps(user_description, ensure_ascii=True)},
                    ],
                }
            ],
            "generationConfig": {"temperature": 0.2},
        }
        return await self._call_with_fallback(payload)

    async def grounded_answer(self, *, query: str, max_citations: int) -> GeminiCallResult:
        prompt = (
            "Use Google Search grounding and answer in concise Japanese. "
            "Include key points and mention at most "
            f"{max_citations} sources with URL-like references when available."
        )
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt},
                        {"text": query},
                    ],
                }
            ],
            "tools": [{"google_search": {}}],
            "generationConfig": {"temperature": 0.3},
        }
        return await self._call_with_fallback(payload)

    async def _call_with_fallback(self, payload: dict[str, Any]) -> GeminiCallResult:
        if not self.available():
            raise RuntimeError("Gemini API key is not configured")

        primary_error = ""
        try:
            text = await self._call_generate_content(model=self._default_model, payload=payload)
            return GeminiCallResult(text=text, model=self._default_model)
        except RuntimeError as exc:
            primary_error = str(exc)

        text = await self._call_generate_content(model=self._fallback_model, payload=payload)
        if not text:
            raise RuntimeError(primary_error or "Gemini returned empty response")
        return GeminiCallResult(text=text, model=self._fallback_model)

    async def _call_generate_content(self, *, model: str, payload: dict[str, Any]) -> str:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            f"?key={self._api_key}"
        )
        req = request.Request(
            url=url,
            method="POST",
            headers={"Content-Type": "application/json"},
            data=body,
        )

        try:
            raw = await asyncio.to_thread(self._open_request, req)
        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError(f"Gemini request failed ({type(exc).__name__})") from exc

        text = self._extract_text(raw)
        if not text:
            raise RuntimeError("Gemini response has no text part")
        return text

    def _open_request(self, req: request.Request) -> dict[str, object]:
        try:
            with request.urlopen(req, timeout=self._timeout) as response:
                body = response.read().decode("utf-8")
        except error.HTTPError as exc:
            raise RuntimeError(f"Gemini HTTP {exc.code}") from exc
        except error.URLError as exc:
            raise RuntimeError(f"Gemini network error ({exc.reason})") from exc

        try:
            payload = json.loads(body)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Gemini response parse error") from exc

        if not isinstance(payload, dict):
            raise RuntimeError("Gemini response is not an object")
        return cast(dict[str, object], payload)

    def _extract_text(self, payload: dict[str, object]) -> str:
        candidates = payload.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            return ""

        first = candidates[0]
        if not isinstance(first, dict):
            return ""

        content = first.get("content")
        if not isinstance(content, dict):
            return ""

        parts = content.get("parts")
        if not isinstance(parts, list):
            return ""

        texts: list[str] = []
        for part in parts:
            if isinstance(part, dict):
                value = part.get("text")
                if isinstance(value, str) and value.strip():
                    texts.append(value.strip())
        return "\n".join(texts)
