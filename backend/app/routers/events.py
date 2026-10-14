"""Events for one baby: /api/babies/{baby_id}/events

Every route depends on `AccessibleBaby`, so the caregiver check happens once,
in app/deps.py, instead of being repeated in each endpoint.
"""

from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, Query, Response, status
from pydantic import AwareDatetime, ValidationError
from sqlalchemy import select

from app.deps import AccessibleBaby, CurrentUser, DbSession
from app.models import Baby, Event, EventType
from app.models.enums import DURATION_EVENT_TYPES
from app.schemas.event import METADATA_SCHEMAS, EventCreate, EventRead, EventUpdate

router = APIRouter(prefix="/babies/{baby_id}/events", tags=["events"])


def _get_event(db: DbSession, baby: Baby, event_id: int) -> Event:
    event = db.scalar(select(Event).where(Event.id == event_id, Event.baby_id == baby.id))
    if event is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@router.get("", response_model=list[EventRead])
def list_events(
    baby: AccessibleBaby,
    db: DbSession,
    event_type: EventType | None = None,
    ongoing: Annotated[
        bool | None, Query(description="Only sleeps/feedings that haven't ended yet")
    ] = None,
    since: AwareDatetime | None = None,
    until: AwareDatetime | None = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> list[Event]:
    # Building a query step by step is like chaining ActiveRecord scopes.
    query = select(Event).where(Event.baby_id == baby.id)
    if event_type is not None:
        query = query.where(Event.event_type == event_type)
    if ongoing:
        query = query.where(Event.ended_at.is_(None), Event.event_type.in_(DURATION_EVENT_TYPES))
    if since is not None:
        query = query.where(Event.started_at >= since)
    if until is not None:
        query = query.where(Event.started_at < until)
    query = query.order_by(Event.started_at.desc()).limit(limit)
    return list(db.scalars(query))


@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create_event(
    baby: AccessibleBaby,
    db: DbSession,
    user: CurrentUser,
    body: Annotated[EventCreate, Body()],
) -> Event:
    event = Event(
        baby_id=baby.id,
        created_by_user_id=user.id,
        event_type=body.event_type,
        started_at=body.started_at,
        ended_at=body.ended_at,
        # exclude_none drops optional fields that weren't given, keeping the JSON tidy
        details=body.metadata.model_dump(exclude_none=True),
    )
    db.add(event)
    db.commit()
    return event


@router.get("/{event_id}", response_model=EventRead)
def get_event(event_id: int, baby: AccessibleBaby, db: DbSession) -> Event:
    return _get_event(db, baby, event_id)


@router.patch("/{event_id}", response_model=EventRead)
def update_event(event_id: int, body: EventUpdate, baby: AccessibleBaby, db: DbSession) -> Event:
    event = _get_event(db, baby, event_id)
    # exclude_unset: only fields actually present in the request body.
    # That's how {"ended_at": null} (clear it) differs from {} (leave it alone).
    changes = body.model_dump(exclude_unset=True)

    if "metadata" in changes:
        schema = METADATA_SCHEMAS[event.event_type]
        try:
            metadata = schema.model_validate(changes.pop("metadata") or {})
        except ValidationError as error:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=error.errors(include_url=False, include_context=False),
            ) from error
        event.details = metadata.model_dump(exclude_none=True)

    if "started_at" in changes and changes["started_at"] is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail="started_at is required")

    for field, value in changes.items():
        setattr(event, field, value)  # like Ruby's public_send("#{field}=", value)

    if event.ended_at is not None and event.ended_at < event.started_at:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, detail="ended_at must be after started_at"
        )

    db.commit()
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, baby: AccessibleBaby, db: DbSession) -> Response:
    db.delete(_get_event(db, baby, event_id))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
