"""Importing every model here registers them all on Base.metadata.

Alembic and the tests import `app.models` so that every table is known,
which is what Rails' autoloading does for you implicitly.
"""

from app.models.baby import Baby
from app.models.caregiving import Caregiving
from app.models.enums import CaregivingRole, EventType, ReminderType, ScheduleKind
from app.models.event import Event
from app.models.milestone import Milestone
from app.models.reminder import Reminder
from app.models.user import User

__all__ = [
    "Baby",
    "Caregiving",
    "CaregivingRole",
    "Event",
    "EventType",
    "Milestone",
    "Reminder",
    "ReminderType",
    "ScheduleKind",
    "User",
]
