from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

from src.models.coworking import CoworkingModel


class CoworkingBookingModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "coworking_bookings"

    student_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False, index=True,
    )
    coworking_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("coworkings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    taken_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
    )
    returned_back: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="created", index=True,
    )

    coworking: Mapped["CoworkingModel"] = relationship(
        "CoworkingModel",
        back_populates="bookings",
    )
