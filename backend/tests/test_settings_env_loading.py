# file: tests/test_settings_env_loading.py
from importlib import import_module

from _pytest.monkeypatch import MonkeyPatch


def test_settings_reads_env_values(monkeypatch: MonkeyPatch) -> None:
    settings_module = import_module("app.core.settings")
    settings_cls = settings_module.Settings

    monkeypatch.setenv("INSTAGRAM_API_VERSION", "v99.0")
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key")

    loaded = settings_cls()
    assert loaded.instagram_api_version == "v99.0"
    assert loaded.gemini_api_key == "dummy-key"
