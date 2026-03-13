from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class DutyReportImageResponse(BaseModel):
    id: UUID = Field(...)
    report_id: UUID = Field(...)
    category_id: UUID = Field(...)
    photo_url: str = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)

    class Config:
        from_attributes = True


class DutyReportImageCreate(BaseModel):
    category_id: UUID = Field(...)
    photo_url: str = Field(...)
