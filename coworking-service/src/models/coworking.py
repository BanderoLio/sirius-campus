from __future__ import annotations

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

from src.models.coworking_booking import CoworkingBookingModel


class CoworkingModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "coworkings"

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    building: Mapped[int] = mapped_column(Integer, nullable=False)
    entrance: Mapped[int] = mapped_column(Integer, nullable=False)
    number: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    bookings: Mapped[list["CoworkingBookingModel"]] = relationship(
        "CoworkingBookingModel",
        back_populates="coworking",
        cascade="all, delete-orphan",
    )
