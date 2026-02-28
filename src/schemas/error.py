"""
Error schemas for auth-service API.
"""
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class ErrorDetail(BaseModel):
    """Error detail schema."""

    code: str
    message: str
    trace_id: Optional[str] = None
    details: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: ErrorDetail


# Common error codes
class AuthErrorCode:
    """Auth service error codes."""

    INVALID_CREDENTIALS = "AUTH_INVALID_CREDENTIALS"
    USER_NOT_FOUND = "AUTH_USER_NOT_FOUND"
    USER_ALREADY_EXISTS = "AUTH_USER_ALREADY_EXISTS"
    INVALID_TOKEN = "AUTH_INVALID_TOKEN"
    TOKEN_EXPIRED = "AUTH_TOKEN_EXPIRED"
    TOKEN_REVOKED = "AUTH_TOKEN_REVOKED"
    REFRESH_TOKEN_INVALID = "AUTH_REFRESH_TOKEN_INVALID"
    INVALID_PASSWORD = "AUTH_INVALID_PASSWORD"
    USER_INACTIVE = "AUTH_USER_INACTIVE"
    USER_NOT_VERIFIED = "AUTH_USER_NOT_VERIFIED"
    ROLE_NOT_FOUND = "AUTH_ROLE_NOT_FOUND"
    STUDENT_NOT_FOUND = "AUTH_STUDENT_NOT_FOUND"
    EDUCATOR_NOT_FOUND = "AUTH_EDUCATOR_NOT_FOUND"
    PROFILE_ALREADY_EXISTS = "AUTH_PROFILE_ALREADY_EXISTS"


class CommonErrorCode:
    """Common error codes."""

    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    INTERNAL_ERROR = "INTERNAL_ERROR"
