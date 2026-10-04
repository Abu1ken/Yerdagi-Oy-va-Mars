"""Application configuration.

Settings are read from environment variables and/or a local ``.env`` file so
that no secret or environment specific value is hard-coded in the source.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly typed application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Earth Analog Finder - Moon & Mars"
    app_version: str = "1.0.0"
    debug: bool = True

    # SQLite only, per project constraints.
    database_url: str = "sqlite:///./analog.db"

    cors_origins: str = "*"

    default_page_size: int = 20
    max_page_size: int = 100

    @property
    def cors_origin_list(self) -> List[str]:
        """Return the configured CORS origins as a clean list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings instance (read once per process)."""
    return Settings()
