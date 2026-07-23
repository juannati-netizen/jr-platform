from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "JR Platform API"
    app_env: str = "development"
    app_version: str = "0.8.0"
    database_url: str = "sqlite+pysqlite:///./jr_platform.db"
    jwt_secret_key: str = "development-secret-change-me-please"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    initial_admin_email: str | None = None
    initial_admin_password: str | None = None
    initial_admin_full_name: str = "JR Platform Admin"
    cors_origins: str = "http://localhost:5173"
    legacy_tariff_csv_path: str = "private-import/tariff_items.csv"
    ai_api_key: str = ""
    ai_base_url: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
