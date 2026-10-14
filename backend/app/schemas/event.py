"""Event schemas.

Each event type has its own metadata shape. Instead of one schema with lots of
optional fields, there's one schema per type and a *discriminated union*:
Pydantic reads `event_type` first and then validates `metadata` with the
matching model. So {"event_type": "diaper", "metadata": {"type": "soup"}}
is rejected with a precise error, and the /docs page shows every variant.
"""

from datetime import datetime
from typing import Annotated, Any, Literal, Self

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

from app.models.enums import EventType

# ---------------------------------------------------------------- metadata ---


class _Metadata(BaseModel):
    # Reject unknown keys, so typos like "quantitiy_ml" don't get silently stored.
    model_config = ConfigDict(extra="forbid")


class SleepMetadata(_Metadata):
    quality: Literal["good", "ok", "bad"] | None = None


class FeedingMetadata(_Metadata):
    type: Literal["breast", "milk", "formula", "solids"]
    quantity_ml: int | None = Field(default=None, ge=0, le=1000)
    side: Literal["left", "right", "both"] | None = None


class DiaperMetadata(_Metadata):
    type: Literal["wet", "poop", "mixed"]


class SymptomMetadata(_Metadata):
    symptom: str = Field(min_length=1, max_length=100)
    temperature: float | None = Field(default=None, ge=30, le=45)
    severity: Literal["mild", "moderate", "severe"] | None = None


class MedicationMetadata(_Metadata):
    name: str = Field(min_length=1, max_length=100)
    dose: str = Field(min_length=1, max_length=50)


METADATA_SCHEMAS: dict[EventType, type[_Metadata]] = {
    EventType.SLEEP: SleepMetadata,
    EventType.FEEDING: FeedingMetadata,
    EventType.DIAPER: DiaperMetadata,
    EventType.SYMPTOM: SymptomMetadata,
    EventType.MEDICATION: MedicationMetadata,
}

# ------------------------------------------------------------------ create ---


class _EventCreateBase(BaseModel):
    # AwareDatetime rejects timestamps without a timezone ("2026-10-14T03:00").
    # Send ISO strings with an offset, e.g. new Date().toISOString() in JS.
    started_at: AwareDatetime
    ended_at: AwareDatetime | None = None

    @model_validator(mode="after")
    def ended_after_started(self) -> Self:
        if self.ended_at is not None and self.ended_at < self.started_at:
            raise ValueError("ended_at must be after started_at")
        return self


class SleepEventCreate(_EventCreateBase):
    event_type: Literal[EventType.SLEEP]
    metadata: SleepMetadata = SleepMetadata()


class FeedingEventCreate(_EventCreateBase):
    event_type: Literal[EventType.FEEDING]
    metadata: FeedingMetadata


class DiaperEventCreate(_EventCreateBase):
    event_type: Literal[EventType.DIAPER]
    metadata: DiaperMetadata


class SymptomEventCreate(_EventCreateBase):
    event_type: Literal[EventType.SYMPTOM]
    metadata: SymptomMetadata


class MedicationEventCreate(_EventCreateBase):
    event_type: Literal[EventType.MEDICATION]
    metadata: MedicationMetadata


EventCreate = Annotated[
    SleepEventCreate
    | FeedingEventCreate
    | DiaperEventCreate
    | SymptomEventCreate
    | MedicationEventCreate,
    Field(discriminator="event_type"),
]

# ------------------------------------------------------------ update/read ---


class EventUpdate(BaseModel):
    """PATCH body. Only the fields you send are changed.

    The common case is stopping a running sleep: {"ended_at": "..."}.
    `metadata` is validated against the event's existing type in the router.
    """

    started_at: AwareDatetime | None = None
    ended_at: AwareDatetime | None = None
    metadata: dict[str, Any] | None = None


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    baby_id: int
    created_by_user_id: int | None
    event_type: EventType
    started_at: datetime
    ended_at: datetime | None
    # Read from the ORM attribute `details` (see the gotcha in models/event.py)
    # but appear as "metadata" in the JSON.
    metadata: dict[str, Any] = Field(validation_alias="details")
    created_at: datetime
