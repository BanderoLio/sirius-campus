from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class ApplicationDocumentModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "application_documents"

    application_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_type: Mapped[str] = mapped_column(String(30), nullable=False)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    uploaded_by: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)

    application: Mapped["ApplicationModel"] = relationship(
        "ApplicationModel",
        back_populates="documents",
    )
