from __future__ import annotations

from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, String, SmallInteger, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class PatrolModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "patrols"

    __table_args__ = (
        CheckConstraint("building IN ('8', '9')", name="ck_patrols_building"),
        CheckConstraint("entrance BETWEEN 1 AND 4", name="ck_patrols_entrance"),
        CheckConstraint("status IN ('in_progress', 'completed')", name="ck_patrols_status"),
        UniqueConstraint("date", "building", "entrance", name="uq_patrols_date_building_entrance"),
    )

    patrol_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    building: Mapped[str] = mapped_column(String(1), nullable=False)
    entrance: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="in_progress", index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    entries: Mapped[list["PatrolEntryModel"]] = relationship(
        "PatrolEntryModel",
        back_populates="patrol",
        cascade="all, delete-orphan",
    )
