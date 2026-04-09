# file: tests/test_search_grounding_integration.py
from importlib import import_module

from fastapi.testclient import TestClient
from _pytest.monkeypatch import MonkeyPatch

app = import_module("app.main").app
client = TestClient(app)


def test_search_grounding_endpoint_contract(monkeypatch: MonkeyPatch) -> None:
    gemini_module = import_module("app.integrations.gemini_client")

    async def fake_grounded_answer(self, **kwargs):  # type: ignore[no-untyped-def]
        return gemini_module.GeminiCallResult(
            text="Grounded answer sample https://example.com/source-a",
            model="gemini-2.5-flash",
        )

    monkeypatch.setattr(gemini_module.GeminiClient, "available", lambda self: True)
    monkeypatch.setattr(gemini_module.GeminiClient, "grounded_answer", fake_grounded_answer)

    response = client.post(
        "/api/v1/search-grounding/answer",
        json={"query": "air jordan resale trend", "max_citations": 3},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["query"] == "air jordan resale trend"
    assert isinstance(payload["data"]["answer"], str)
    assert isinstance(payload["data"]["citations"], list)
    assert payload["source"].startswith("grounded-search:")
    assert payload["ai_available"] is True
    assert payload["partial"] is False
