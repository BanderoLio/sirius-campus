from pydantic import BaseModel, Field
from uuid import UUID
from datetime import date, datetime
from typing import List, Optional
from enum import Enum


class DutyStatus(str, Enum):
    pending = "pending"
    active = "active"
    accepted = "accepted"
    overdue = "overdue"


class DutyScheduleResponse(BaseModel):
    id: UUID = Field(...)
    room_id: UUID = Field(...)
    duty_date: date = Field(...)
    assigned_by: UUID = Field(...)
    status: DutyStatus = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)

    class Config:
        from_attributes = True


class DutyScheduleCreate(BaseModel):
    room_id: UUID = Field(...)
    duty_date: date = Field(...)


class DutyScheduleUpdate(BaseModel):
    room_id: UUID = Field(...)
    duty_date: date = Field(...)
    status: DutyStatus = Field(...)


class DutySchedulePatch(BaseModel):
    status: Optional[DutyStatus] = Field(None)


class DutyScheduleListResponse(BaseModel):
    items: List[DutyScheduleResponse] = Field(...)
    total: int = Field(...)
    page: int = Field(...)
    size: int = Field(...)
    pages: int = Field(...)
