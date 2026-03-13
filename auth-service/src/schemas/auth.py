"""
Pydantic schemas for auth-service API.
"""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Base schemas
class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    patronymic: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)


# Request schemas
class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str = Field(..., min_length=8, max_length=100)


class StudentCreate(UserCreate):
    """Schema for creating a student."""

    building: int = Field(..., ge=1, le=20)
    entrance: int = Field(..., ge=1, le=10)
    floor: int = Field(..., ge=1, le=10)
    room: int = Field(..., ge=1, le=9999)
    is_adult: bool = False


class EducatorCreate(UserCreate):
    """Schema for creating an educator."""

    is_night: bool = False


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    patronymic: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    password: Optional[str] = Field(None, min_length=8, max_length=100)


class StudentUpdate(UserUpdate):
    """Schema for updating a student."""

    building: Optional[int] = Field(None, ge=1, le=20)
    entrance: Optional[int] = Field(None, ge=1, le=10)
    floor: Optional[int] = Field(None, ge=1, le=10)
    room: Optional[int] = Field(None, ge=1, le=9999)
    is_adult: Optional[bool] = None


class EducatorUpdate(UserUpdate):
    """Schema for updating an educator."""

    is_night: Optional[bool] = None


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""

    refresh_token: str


# Response schemas
class UserResponse(BaseModel):
    """Schema for user response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    first_name: str
    last_name: str
    patronymic: Optional[str]
    phone: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class StudentResponse(BaseModel):
    """Schema for student response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    building: int
    entrance: int
    floor: int
    room: int
    is_adult: bool
    created_at: datetime
    updated_at: datetime
    phone: Optional[str] = None


class EducatorResponse(BaseModel):
    """Schema for educator response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    is_night: bool
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    """Schema for token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserWithProfile(BaseModel):
    """Schema for user with profile."""

    user: UserResponse
    profile: Optional[StudentResponse | EducatorResponse]
    user_type: str


class PaginatedUsersResponse(BaseModel):
    """Schema for paginated users response."""

    items: list[UserResponse]
    total: int
    page: int
    size: int
    pages: int


class PaginatedStudentsResponse(BaseModel):
    """Schema for paginated students response."""

    items: list[StudentResponse]
    total: int
    page: int
    size: int
    pages: int


class PaginatedEducatorsResponse(BaseModel):
    """Schema for paginated educators response."""

    items: list[EducatorResponse]
    total: int
    page: int
    size: int
    pages: int
