from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.caregiving import Caregiving
    from app.models.event import Event
    from app.models.milestone import Milestone
    from app.models.reminder import Reminder


class Baby(TimestampMixin, Base):
    __tablename__ = "babies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    birth_date: Mapped[date] = mapped_column(Date)

    # cascade="all, delete-orphan" ~ Rails' `dependent: :destroy`
    caregivings: Mapped[list["Caregiving"]] = relationship(
        back_populates="baby", cascade="all, delete-orphan"
    )
    events: Mapped[list["Event"]] = relationship(
        back_populates="baby", cascade="all, delete-orphan"
    )
    milestones: Mapped[list["Milestone"]] = relationship(
        back_populates="baby", cascade="all, delete-orphan"
    )
    reminders: Mapped[list["Reminder"]] = relationship(
        back_populates="baby", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Baby id={self.id} name={self.name!r}>"
