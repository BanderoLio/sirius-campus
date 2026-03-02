from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Text, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin


class PatrolEntryModel(Base, TimestampMixin):
    __tablename__ = "patrol_entries"

    __table_args__ = (
        UniqueConstraint("patrol_id", "user_id", name="uq_patrol_entries_patrol_user"),
    )

    patrol_entry_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    patrol_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("patrols.patrol_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    room: Mapped[str] = mapped_column(String(10), nullable=False)
    is_present: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    absence_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    patrol: Mapped["PatrolModel"] = relationship(
        "PatrolModel",
        back_populates="entries",
    )


# Import here to avoid circular imports
from src.models.patrol import PatrolModel
