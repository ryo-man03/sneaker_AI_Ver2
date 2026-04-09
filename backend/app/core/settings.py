# file: app/core/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SOLE//MATRIX API"
    app_version: str = "0.1.0"
    jwt_secret_key: str = "change-me-in-env"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    demo_user_email: str = "yamada@example.com"
    demo_user_password: str = "password123"
    google_api_key: str = ""
    gemini_api_key: str = ""
    instagram_access_token: str = ""
    instagram_business_account_id: str = ""
    instagram_api_version: str = "v25.0"
    gemini_default_model: str = "gemini-2.5-flash"
    gemini_fallback_model: str = "gemini-2.5-pro"
    gemini_timeout_seconds: int = 20
    instagram_timeout_seconds: int = 10
    database_url: str = "sqlite+aiosqlite:///./sole_matrix.db"
    sqlite_busy_timeout_ms: int = 5000
    alert_scheduler_enabled: bool = True
    alert_scheduler_interval_seconds: int = 60
    notification_center_default_limit: int = 50

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def resolved_google_api_key(self) -> str:
        return self.google_api_key or self.gemini_api_key


settings = Settings()
