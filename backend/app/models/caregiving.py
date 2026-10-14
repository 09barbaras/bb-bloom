from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, TimestampMixin
from app.models.enums import CaregivingRole, str_enum_column

if TYPE_CHECKING:
    from app.models.baby import Baby
    from app.models.user import User


class Caregiving(TimestampMixin, Base):
    """Join model between User and Baby (has_many :babies, through: :caregivings)."""

    __tablename__ = "caregivings"
    __table_args__ = (UniqueConstraint("user_id", "baby_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    baby_id: Mapped[int] = mapped_column(ForeignKey("babies.id", ondelete="CASCADE"), index=True)
    role: Mapped[CaregivingRole] = mapped_column(str_enum_column(CaregivingRole))
    invited_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # NULL until the invited caregiver accepts. `X | None` means "nullable".
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="caregivings")
    baby: Mapped["Baby"] = relationship(back_populates="caregivings")
