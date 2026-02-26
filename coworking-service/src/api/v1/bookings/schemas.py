from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.api.v1.coworkings.schemas import CoworkingResponse


class BookingCreateRequest(BaseModel):
    coworking_id: UUID
    taken_from: datetime
    returned_back: datetime


class StudentShort(BaseModel):
    user_id: str
    last_name: str
    first_name: str
    patronymic: str | None = None
    building: int
    entrance: int
    room: str


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    student_id: UUID
    coworking_id: UUID
    taken_from: datetime
    returned_back: datetime
    status: str


class BookingDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    student_id: UUID
    coworking_id: UUID
    taken_from: datetime
    returned_back: datetime
    status: str
    student: StudentShort | None = None
    coworking: CoworkingResponse | None = None


class BookingListResponse(BaseModel):
    items: list[BookingDetailResponse]
    total: int
    limit: int
    offset: int
