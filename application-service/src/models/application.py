from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String, Text, Boolean, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class ApplicationModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "applications"

    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    is_minor: Mapped[bool] = mapped_column(Boolean, nullable=False)
    leave_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    return_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    contact_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    decided_by: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reject_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    documents: Mapped[list["ApplicationDocumentModel"]] = relationship(
        "ApplicationDocumentModel",
        back_populates="application",
        cascade="all, delete-orphan",
    )
