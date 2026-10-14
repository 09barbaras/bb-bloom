from typing import TYPE_CHECKING, Any

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, TimestampMixin

# Imports only for the type checker; avoids circular imports at runtime.
if TYPE_CHECKING:
    from app.models.caregiving import Caregiving


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_digest: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(100))
    # e.g. {"feeding_interval_minutes": 180, "quiet_hours": ["22:00", "06:00"]}
    notification_preferences: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, server_default="{}"
    )

    caregivings: Mapped[list["Caregiving"]] = relationship(back_populates="user")

    def __repr__(self) -> str:  # like Ruby's #inspect
        return f"<User id={self.id} email={self.email!r}>"
