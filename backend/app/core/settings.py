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
    gemini_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
