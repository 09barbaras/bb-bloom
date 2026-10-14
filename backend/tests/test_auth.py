from fastapi.testclient import TestClient

from tests.conftest import signup


def test_signup_then_me(client: TestClient):
    headers = signup(client, email="Ana@Example.com")

    response = client.get("/api/auth/me", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "ana@example.com"  # stored lowercased
    assert "password_digest" not in body  # never leaks through the schema


def test_signup_rejects_duplicate_email(client: TestClient):
    signup(client)
    response = client.post(
        "/api/auth/signup",
        json={"email": "ana@example.com", "password": "another-pass", "name": "Ana 2"},
    )
    assert response.status_code == 409


def test_signup_validates_input(client: TestClient):
    response = client.post(
        "/api/auth/signup", json={"email": "not-an-email", "password": "short", "name": ""}
    )
    assert response.status_code == 422
    failing_fields = {error["loc"][-1] for error in response.json()["detail"]}
    assert failing_fields == {"email", "password", "name"}


def test_login_with_form(client: TestClient):
    signup(client)

    ok = client.post(
        "/api/auth/token", data={"username": "ana@example.com", "password": "s3cret-pass"}
    )
    wrong = client.post("/api/auth/token", data={"username": "ana@example.com", "password": "nope"})

    assert ok.status_code == 200
    assert ok.json()["token_type"] == "bearer"
    assert wrong.status_code == 401


def test_me_requires_a_valid_token(client: TestClient):
    assert client.get("/api/auth/me").status_code == 401
    bad = client.get("/api/auth/me", headers={"Authorization": "Bearer garbage"})
    assert bad.status_code == 401
