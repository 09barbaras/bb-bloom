"""Shared pytest fixtures (pytest's version of RSpec's let / before blocks).

Tests run against a real Postgres database (TEST_DATABASE_URL) because the app
uses Postgres-only features like JSONB. Each test runs inside a transaction that
is rolled back afterwards, so tests never see each other's data, the same idea
as Rails' transactional tests.
"""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import app.models  # noqa: F401  (registers all tables)
from app.config import get_settings
from app.db import Base, get_db
from app.main import app


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(get_settings().test_database_url)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)  # a fresh schema per test run, straight from the models
    yield engine
    engine.dispose()


@pytest.fixture
def db(engine) -> Iterator[Session]:
    connection = engine.connect()
    transaction = connection.begin()
    # "create_savepoint" lets the app call db.commit() freely: the commits become
    # savepoints inside our outer transaction, which we roll back at the end.
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db: Session) -> Iterator[TestClient]:
    # Swap the real get_db dependency for one that returns the test session.
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def signup(client: TestClient, email: str = "ana@example.com", name: str = "Ana") -> dict:
    """Create a user and return the Authorization header for them."""
    response = client.post(
        "/api/auth/signup", json={"email": email, "password": "s3cret-pass", "name": name}
    )
    assert response.status_code == 201, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def auth_headers(client: TestClient) -> dict:
    return signup(client)


@pytest.fixture
def baby_id(client: TestClient, auth_headers: dict) -> int:
    response = client.post(
        "/api/babies", json={"name": "Leo", "birth_date": "2026-08-01"}, headers=auth_headers
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]
