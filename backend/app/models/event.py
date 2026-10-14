from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, TimestampMixin
from app.models.enums import EventType, str_enum_column

if TYPE_CHECKING:
    from app.models.baby import Baby
    from app.models.user import User


class Event(TimestampMixin, Base):
    __tablename__ = "events"
    __table_args__ = (
        # Most queries are "this baby's events, newest first".
        Index("ix_events_baby_id_started_at", "baby_id", "started_at"),
        CheckConstraint("ended_at IS NULL OR ended_at >= started_at", name="ended_after_started"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    baby_id: Mapped[int] = mapped_column(ForeignKey("babies.id", ondelete="CASCADE"))
    created_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    event_type: Mapped[EventType] = mapped_column(str_enum_column(EventType))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    # NULL means either "instantaneous" (diaper) or "still ongoing" (sleep in progress).
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # GOTCHA: `metadata` is a reserved attribute on SQLAlchemy models (it holds the
    # table definitions). So the Python attribute is `details`, while the database
    # column and the JSON field in the API are still called "metadata".
    details: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, default=dict, server_default="{}"
    )

    baby: Mapped["Baby"] = relationship(back_populates="events")
    created_by: Mapped["User | None"] = relationship()
