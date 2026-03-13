from pydantic import BaseModel, Field
from uuid import UUID
from typing import List


class DutyCategoryResponse(BaseModel):
    id: UUID = Field(...)
    name: str = Field(...)

    class Config:
        from_attributes = True


class DutyCategoryListResponse(BaseModel):
    items: List[DutyCategoryResponse] = Field(...)
    total: int = Field(...)
    page: int = Field(...)
    size: int = Field(...)
    pages: int = Field(...)
