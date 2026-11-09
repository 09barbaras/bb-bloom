from sqlalchemy import create_engine, text

from app.config import settings


def test_can_connect_to_test_database():
    engine = create_engine(settings.test_database_url)

    with engine.connect() as connection:
        assert connection.execute(text("select current_database()")).scalar() == "bb_bloom_test"
