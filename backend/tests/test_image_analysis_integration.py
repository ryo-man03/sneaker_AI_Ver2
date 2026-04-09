# file: tests/test_image_analysis_integration.py
from importlib import import_module

from fastapi.testclient import TestClient
from _pytest.monkeypatch import MonkeyPatch

app = import_module("app.main").app
client = TestClient(app)


def test_image_analysis_endpoint_contract(monkeypatch: MonkeyPatch) -> None:
    gemini_module = import_module("app.integrations.gemini_client")

    async def fake_analyze_image(self, **kwargs):  # type: ignore[no-untyped-def]
        return gemini_module.GeminiCallResult(
            text=(
                '{"is_sneaker": true, "brand": "NIKE", "model": "Jordan 1", '
                '"colorway": "Bred", "material": "Leather", '
                '"notes": ["mock"], "confidence": 0.91}'
            ),
            model="gemini-2.5-flash",
        )

    monkeypatch.setattr(gemini_module.GeminiClient, "available", lambda self: True)
    monkeypatch.setattr(gemini_module.GeminiClient, "analyze_image", fake_analyze_image)

    response = client.post(
        "/api/v1/image-analysis/analyze",
        json={
            "image_url": "https://example.com/sneaker.jpg",
            "hint_text": "nike jordan",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["is_sneaker"] is True
    assert payload["data"]["brand"] == "NIKE"
    assert payload["source"].startswith("gemini:")
    assert payload["ai_available"] is True
    assert "updated_at" in payload
    assert "partial" in payload
