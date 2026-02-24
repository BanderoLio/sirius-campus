from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PatrolCreateRequest(BaseModel):
    date: date
    building: str = Field(..., pattern="^(8|9)$")
    entrance: int = Field(..., ge=1, le=4)


class PatrolUpdateRequest(BaseModel):
    status: str = Field(..., pattern="^completed$")


class PatrolEntryUpdateRequest(BaseModel):
    is_present: bool | None = None
    absence_reason: str | None = Field(None, max_length=2000)


class PatrolEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    patrol_entry_id: UUID
    patrol_id: UUID
    user_id: UUID
    room: str
    is_present: bool | None
    absence_reason: str | None
    checked_at: datetime | None
    created_at: datetime
    updated_at: datetime


class PatrolResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    patrol_id: UUID
    date: date
    building: str
    entrance: int
    status: str
    started_at: datetime
    submitted_at: datetime | None
    created_at: datetime
    updated_at: datetime


class PatrolDetailResponse(PatrolResponse):
    entries: list[PatrolEntryResponse] = []


class PatrolListResponse(BaseModel):
    items: list[PatrolResponse]
    total: int
    page: int
    size: int
    pages: int


class ErrorResponse(BaseModel):
    error: "ErrorDetail"


class ErrorDetail(BaseModel):
    code: str
    message: str
    trace_id: str | None = None
    details: dict | None = None
