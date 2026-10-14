from fastapi.testclient import TestClient

from tests.conftest import signup


def events_url(baby_id: int) -> str:
    return f"/api/babies/{baby_id}/events"


def test_log_a_feeding(client: TestClient, auth_headers: dict, baby_id: int):
    response = client.post(
        events_url(baby_id),
        json={
            "event_type": "feeding",
            "started_at": "2026-10-14T03:10:00+01:00",
            "ended_at": "2026-10-14T03:30:00+01:00",
            "metadata": {"type": "milk", "quantity_ml": 120},
        },
        headers=auth_headers,
    )

    assert response.status_code == 201, response.text
    event = response.json()
    assert event["metadata"] == {"type": "milk", "quantity_ml": 120}
    assert event["created_by_user_id"] is not None
    # Postgres stores UTC; the offset you sent is converted, not lost.
    assert event["started_at"].startswith("2026-10-14T02:10:00")


def test_metadata_is_validated_per_event_type(client: TestClient, auth_headers: dict, baby_id: int):
    response = client.post(
        events_url(baby_id),
        json={
            "event_type": "diaper",
            "started_at": "2026-10-14T03:10:00Z",
            "metadata": {"type": "soup"},
        },
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_naive_datetimes_are_rejected(client: TestClient, auth_headers: dict, baby_id: int):
    response = client.post(
        events_url(baby_id),
        json={"event_type": "sleep", "started_at": "2026-10-14T03:10:00"},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_start_and_stop_a_sleep(client: TestClient, auth_headers: dict, baby_id: int):
    started = client.post(
        events_url(baby_id),
        json={"event_type": "sleep", "started_at": "2026-10-14T20:00:00Z"},
        headers=auth_headers,
    ).json()

    ongoing = client.get(events_url(baby_id), params={"ongoing": True}, headers=auth_headers)
    assert [event["id"] for event in ongoing.json()] == [started["id"]]

    stopped = client.patch(
        f"{events_url(baby_id)}/{started['id']}",
        json={"ended_at": "2026-10-14T22:30:00Z", "metadata": {"quality": "good"}},
        headers=auth_headers,
    )
    assert stopped.status_code == 200, stopped.text
    assert stopped.json()["metadata"] == {"quality": "good"}

    ongoing = client.get(events_url(baby_id), params={"ongoing": True}, headers=auth_headers)
    assert ongoing.json() == []


def test_cannot_end_before_starting(client: TestClient, auth_headers: dict, baby_id: int):
    event = client.post(
        events_url(baby_id),
        json={"event_type": "sleep", "started_at": "2026-10-14T20:00:00Z"},
        headers=auth_headers,
    ).json()

    response = client.patch(
        f"{events_url(baby_id)}/{event['id']}",
        json={"ended_at": "2026-10-14T19:00:00Z"},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_list_filters_and_orders_newest_first(client: TestClient, auth_headers: dict, baby_id: int):
    for hour, event_type, metadata in [
        ("01", "diaper", {"type": "wet"}),
        ("02", "medication", {"name": "paracetamol", "dose": "2.5ml"}),
        ("03", "diaper", {"type": "poop"}),
    ]:
        client.post(
            events_url(baby_id),
            json={
                "event_type": event_type,
                "started_at": f"2026-10-14T{hour}:00:00Z",
                "metadata": metadata,
            },
            headers=auth_headers,
        )

    diapers = client.get(
        events_url(baby_id), params={"event_type": "diaper"}, headers=auth_headers
    ).json()

    assert [event["metadata"]["type"] for event in diapers] == ["poop", "wet"]


def test_delete_event(client: TestClient, auth_headers: dict, baby_id: int):
    event = client.post(
        events_url(baby_id),
        json={
            "event_type": "diaper",
            "started_at": "2026-10-14T03:00:00Z",
            "metadata": {"type": "wet"},
        },
        headers=auth_headers,
    ).json()

    url = f"{events_url(baby_id)}/{event['id']}"
    assert client.delete(url, headers=auth_headers).status_code == 204
    assert client.get(url, headers=auth_headers).status_code == 404


def test_strangers_cannot_log_events(client: TestClient, baby_id: int):
    stranger = signup(client, email="stranger@example.com", name="Stranger")
    response = client.post(
        events_url(baby_id),
        json={"event_type": "sleep", "started_at": "2026-10-14T20:00:00Z"},
        headers=stranger,
    )
    assert response.status_code == 404
