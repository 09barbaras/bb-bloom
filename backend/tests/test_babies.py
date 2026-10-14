from fastapi.testclient import TestClient

from tests.conftest import signup


def test_create_and_list_babies(client: TestClient, auth_headers: dict, baby_id: int):
    response = client.get("/api/babies", headers=auth_headers)

    assert response.status_code == 200
    assert [baby["id"] for baby in response.json()] == [baby_id]


def test_birth_date_cannot_be_in_the_future(client: TestClient, auth_headers: dict):
    response = client.post(
        "/api/babies", json={"name": "Future", "birth_date": "2999-01-01"}, headers=auth_headers
    )
    assert response.status_code == 422


def test_other_users_cannot_see_the_baby(client: TestClient, baby_id: int):
    stranger = signup(client, email="stranger@example.com", name="Stranger")

    assert client.get("/api/babies", headers=stranger).json() == []
    assert client.get(f"/api/babies/{baby_id}", headers=stranger).status_code == 404
