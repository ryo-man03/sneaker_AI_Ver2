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
    cors_allow_origins: str = "http://127.0.0.1:5173,http://localhost:5173"
    cors_allow_credentials: bool = False
    trusted_hosts: str = "127.0.0.1,localhost,testserver"
    security_headers_enabled: bool = True
    maintenance_key_rotation_days: int = 90
    maintenance_dependency_audit_days: int = 30
    maintenance_release_channel: str = "stable"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def resolved_google_api_key(self) -> str:
        return self.google_api_key or self.gemini_api_key

    @property
    def cors_allow_origins_list(self) -> list[str]:
        values = [item.strip() for item in self.cors_allow_origins.split(",")]
        return [item for item in values if item]

    @property
    def trusted_hosts_list(self) -> list[str]:
        values = [item.strip() for item in self.trusted_hosts.split(",")]
        return [item for item in values if item]


settings = Settings()
