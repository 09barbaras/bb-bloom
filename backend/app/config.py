"""App settings, read from environment variables (or a .env file).

Rails equivalent: config/database.yml + credentials + ENV lookups.
pydantic-settings matches each field to an env var with the same name
(case-insensitive), so DATABASE_URL in the environment fills `database_url`.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/bb_bloom"
    test_database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/bb_bloom_test"

    # Change this in any real deployment: it signs the login tokens.
    secret_key: str = "dev-only-secret-change-me-in-production-0123456789"
    access_token_expire_minutes: int = 60 * 24 * 7  # a week; parents shouldn't log in at 3am

    # Origins allowed to call the API from a browser (the React dev server).
    cors_origins: list[str] = ["http://localhost:5173"]


@lru_cache  # build the settings once and reuse them (like a memoized class method)
def get_settings() -> Settings:
    return Settings()
