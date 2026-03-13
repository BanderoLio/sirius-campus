from pydantic import BaseModel, Field
from uuid import uuid4, UUID
from typing import Optional


class ErrorDetail(BaseModel):
    code: str = Field(...)
    message: str = Field(...)
    trace_id: UUID = Field(default_factory=uuid4)
    details: Optional[dict] = Field(None)


class ErrorResponse(BaseModel):
    error: ErrorDetail = Field(...)
