from typing import Final

BOOKING_STATUS_CREATED: Final[str] = "created"
BOOKING_STATUS_ACTIVE: Final[str] = "active"
BOOKING_STATUS_COMPLETED: Final[str] = "completed"
BOOKING_STATUS_CANCELLED: Final[str] = "cancelled"

ALL_BOOKING_STATUSES: Final[tuple[str, ...]] = (
    BOOKING_STATUS_CREATED,
    BOOKING_STATUS_ACTIVE,
    BOOKING_STATUS_COMPLETED,
    BOOKING_STATUS_CANCELLED,
)
