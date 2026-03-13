from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from enum import Enum
from .duty_image import DutyReportImageResponse


class ReportStatus(str, Enum):
    submitted = "submitted"
    accepted = "accepted"
    rejected = "rejected"


class DutyReportResponse(BaseModel):
    id: UUID = Field(...)
    schedule_id: UUID = Field(...)
    user_id: UUID = Field(...)
    status: ReportStatus = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
    reviewed_by: Optional[UUID] = Field(None)
    reviewed_at: Optional[datetime] = Field(None)
    reject_reason: Optional[str] = Field(None)

    class Config:
        from_attributes = True


class DutyReportCreate(BaseModel):
    schedule_id: UUID = Field(...)


class DutyReportUpdate(BaseModel):
    schedule_id: UUID = Field(...)
    status: ReportStatus = Field(...)


class DutyReportPatch(BaseModel):
    status: Optional[ReportStatus] = Field(None)
    reject_reason: Optional[str] = Field(None)


class DutyReportListResponse(BaseModel):
    items: List[DutyReportResponse] = Field(...)
    total: int = Field(...)
    page: int = Field(...)
    size: int = Field(...)
    pages: int = Field(...)


class DutyReportDetailResponse(DutyReportResponse):
    images: List[DutyReportImageResponse] = Field(default_factory=list)
