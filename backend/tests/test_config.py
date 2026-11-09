from app.config import Settings


def test_settings_read_from_environment(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@example:5432/other")

    assert Settings().database_url == "postgresql+psycopg://u:p@example:5432/other"
