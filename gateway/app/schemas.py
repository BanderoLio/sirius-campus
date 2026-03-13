import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# Российский номер: цифры, длина 10–11 (с ведущей 7 или 8 или без)
_PHONE_PATTERN = re.compile(r"^[78]?\d{10}$")


class ApplicationCreateRequest(BaseModel):
    leave_time: datetime
    return_time: datetime
    reason: str = Field(..., min_length=1, max_length=2000)
    contact_phone: str = Field(..., min_length=1, max_length=20)

    @field_validator("contact_phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        digits = re.sub(r"\D", "", v)
        if not _PHONE_PATTERN.match(digits):
            raise ValueError("Некорректный формат телефона")
        return v

    @model_validator(mode="after")
    def validate_dates(self):
        if self.return_time < self.leave_time:
            raise ValueError("Дата возвращения должна быть не раньше даты выхода")
        for name, dt in (("leave_time", self.leave_time), ("return_time", self.return_time)):
            year = dt.year if hasattr(dt, "year") else dt.replace(tzinfo=None).year
            if year < 2000 or year > 2100:
                raise ValueError("Дата должна быть в диапазоне 2000–2100")
        return self


class ApplicationDecideRequest(BaseModel):
    status: str = Field(..., pattern="^(approved|rejected)$")
    reject_reason: str | None = Field(None, max_length=2000)


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    application_id: UUID
    document_type: str
    file_url: str
    uploaded_by: UUID
    created_at: datetime


class DocumentDownloadResponse(BaseModel):
    url: str


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    is_minor: bool
    leave_time: datetime
    return_time: datetime
    reason: str
    contact_phone: str
    status: str
    decided_by: UUID | None
    decided_at: datetime | None
    reject_reason: str | None
    created_at: datetime
    updated_at: datetime
    user_name: str | None = None
    room: str | None = None
    entrance: int | None = None


class ApplicationDetailResponse(ApplicationResponse):
    documents: list[DocumentResponse] = []
    can_decide: bool = False


class ApplicationListResponse(BaseModel):
    items: list[ApplicationResponse]
    total: int
    page: int
    size: int
    pages: int
