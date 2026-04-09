# file: tests/test_instagram_trends_integration.py
from datetime import UTC, datetime
from importlib import import_module

from fastapi.testclient import TestClient
from _pytest.monkeypatch import MonkeyPatch

app = import_module("app.main").app
client = TestClient(app)


def test_instagram_trends_endpoint_contract(monkeypatch: MonkeyPatch) -> None:
    instagram_module = import_module("app.integrations.instagram_client")

    async def fake_fetch_hashtag_trends(self, **kwargs):  # type: ignore[no-untyped-def]
        return [
            instagram_module.InstagramMedia(
                caption="mock trend",
                media_type="IMAGE",
                permalink="https://instagram.com/p/mock",
                like_count=120,
                comments_count=8,
                timestamp=datetime.now(UTC),
            )
        ]

    monkeypatch.setattr(instagram_module.InstagramClient, "available", lambda self: True)
    monkeypatch.setattr(instagram_module.InstagramClient, "fetch_hashtag_trends", fake_fetch_hashtag_trends)

    response = client.get("/api/v1/instagram/trends", params={"hashtag": "sneakers", "limit": 5})
    assert response.status_code == 200

    payload = response.json()
    assert payload["data"]["query"] == "sneakers"
    assert payload["data"]["total"] >= 1
    assert payload["data"]["items"][0]["hashtag"].startswith("#")
    assert payload["source"] == "instagram"
    assert payload["ai_available"] is True
    assert payload["partial"] is False
