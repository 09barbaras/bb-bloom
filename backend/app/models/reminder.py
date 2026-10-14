from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, Integer, String, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, TimestampMixin
from app.models.enums import ReminderType, ScheduleKind, str_enum_column

if TYPE_CHECKING:
    from app.models.baby import Baby
    from app.models.user import User


class Reminder(TimestampMixin, Base):
    __tablename__ = "reminders"
    __table_args__ = (
        # Each schedule kind needs its own field filled in.
        CheckConstraint(
            "schedule_kind != 'relative_to_last_event' OR relative_interval_minutes IS NOT NULL",
            name="relative_needs_interval",
        ),
        CheckConstraint(
            "schedule_kind != 'fixed_recurrence' OR recurrence_rule IS NOT NULL",
            name="recurrence_needs_rule",
        ),
        CheckConstraint(
            "schedule_kind != 'course' OR course_end_date IS NOT NULL",
            name="course_needs_end_date",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    baby_id: Mapped[int] = mapped_column(ForeignKey("babies.id", ondelete="CASCADE"), index=True)
    created_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    reminder_type: Mapped[ReminderType] = mapped_column(str_enum_column(ReminderType))
    label: Mapped[str | None] = mapped_column(String(200))
    schedule_kind: Mapped[ScheduleKind] = mapped_column(str_enum_column(ScheduleKind))
    relative_interval_minutes: Mapped[int | None] = mapped_column(Integer)
    recurrence_rule: Mapped[str | None] = mapped_column(String(200))
    course_end_date: Mapped[date | None] = mapped_column(Date)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())

    baby: Mapped["Baby"] = relationship(back_populates="reminders")
    created_by: Mapped["User | None"] = relationship()
