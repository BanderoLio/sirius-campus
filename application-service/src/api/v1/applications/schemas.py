from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ApplicationCreateRequest(BaseModel):
    leave_time: datetime
    return_time: datetime
    reason: str = Field(..., min_length=1, max_length=2000)
    contact_phone: str = Field(..., min_length=1, max_length=20)


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


class ApplicationDetailResponse(ApplicationResponse):
    documents: list[DocumentResponse] = []


class ApplicationListResponse(BaseModel):
    items: list[ApplicationResponse]
    total: int
    page: int
    size: int
    pages: int


class PaginatedParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Page size")
