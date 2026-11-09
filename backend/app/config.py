from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Defaults match the Postgres from docker-compose.yml; override in backend/.env.
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/bb_bloom"
    test_database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/bb_bloom_test"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
