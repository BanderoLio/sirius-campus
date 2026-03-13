from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class PatrolEntryResponse(BaseModel):
    patrol_entry_id: UUID
    patrol_id: UUID
    user_id: UUID
    user_name: str | None = None
    room: str
    is_present: bool | None
    absence_reason: str | None
    checked_at: datetime | None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class PatrolResponse(BaseModel):
    patrol_id: UUID
    date: date
    building: str
    entrance: str
    patrol_by: UUID
    status: str
    started_at: datetime
    submitted_at: datetime | None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class PatrolDetailResponse(PatrolResponse):
    entries: list[PatrolEntryResponse] = []


class PatrolListResponse(BaseModel):
    items: list[PatrolResponse]
    total: int
    page: int
    size: int
    pages: int


class PatrolCreateRequest(BaseModel):
    date: date
    building: str
    entrance: str


class PatrolUpdateRequest(BaseModel):
    status: str


class PatrolEntryUpdateRequest(BaseModel):
    is_present: bool
    absence_reason: str | None = None
