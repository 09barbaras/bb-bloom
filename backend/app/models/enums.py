"""Enums shared by models and API schemas.

StrEnum members compare equal to their string values (EventType.SLEEP == "sleep"),
so they serialize to JSON and the database as plain strings.
"""

from enum import StrEnum

from sqlalchemy import Enum


class CaregivingRole(StrEnum):
    OWNER = "owner"
    CAREGIVER = "caregiver"


class EventType(StrEnum):
    SLEEP = "sleep"
    FEEDING = "feeding"
    DIAPER = "diaper"
    SYMPTOM = "symptom"
    MEDICATION = "medication"


# Types that last a while. For these, ended_at = NULL means "still going";
# for the others (a diaper change) it just means "instantaneous".
DURATION_EVENT_TYPES = frozenset({EventType.SLEEP, EventType.FEEDING})


class ReminderType(StrEnum):
    FEEDING = "feeding"
    NAIL_TRIM = "nail_trim"
    MEDICATION = "medication"
    CUSTOM = "custom"


class ScheduleKind(StrEnum):
    RELATIVE_TO_LAST_EVENT = "relative_to_last_event"
    FIXED_RECURRENCE = "fixed_recurrence"
    COURSE = "course"


def str_enum_column(enum_cls: type[StrEnum]) -> Enum:
    """Store an enum as a VARCHAR plus a CHECK constraint.

    Native Postgres ENUM types are awkward to change in migrations, so a plain
    string column with a check constraint is the friendlier choice.
    """
    return Enum(
        enum_cls,
        native_enum=False,
        create_constraint=True,
        length=32,
        values_callable=lambda e: [member.value for member in e],
    )
