from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_database_url(value: str) -> str:
    """Use psycopg 3 for generic PostgreSQL connection strings."""
    if value.startswith("postgres://"):
        return value.replace("postgres://", "postgresql+psycopg://", 1)
    if value.startswith("postgresql://"):
        return value.replace("postgresql://", "postgresql+psycopg://", 1)
    return value


class Settings(BaseSettings):
    app_name: str = "JR Platform API"
    app_env: str = "development"
    app_version: str = "0.12.0"
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
    portal_dist_path: str = "apps/portal/dist"
    security_headers_enabled: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("database_url", mode="before")
    @classmethod
    def validate_database_url(cls, value: object) -> object:
        if isinstance(value, str):
            return normalize_database_url(value)
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
