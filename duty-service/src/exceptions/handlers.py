from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from uuid import UUID, uuid4

from src.constants import (
    INTERNAL_ERROR,
    NOT_FOUND,
    CONFLICT,
    FORBIDDEN,
    UNAUTHORIZED,
    VALIDATION_ERROR,
    AUTH_SERVICE_UNAVAILABLE,
)
from src.exceptions import (
    DutyServiceException,
    NotFoundException,
    ConflictException,
    ForbiddenException,
    UnauthorizedException,
    AuthServiceUnavailableException,
)
from src.schemas import ErrorResponse, ErrorDetail
from src.tracing import trace_id_var


def _build_error_response(status_code: int, code: str, message: str) -> JSONResponse:
    trace_value = trace_id_var.get()
    try:
        trace_id = UUID(trace_value) if trace_value else uuid4()
    except ValueError:
        trace_id = uuid4()
    payload = ErrorResponse(
        error=ErrorDetail(
            code=code,
            message=message,
            trace_id=trace_id,
            details=None,
        )
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump(mode="json"))


async def duty_exception_handler(_: Request, exc: DutyServiceException) -> JSONResponse:
    if isinstance(exc, NotFoundException):
        return _build_error_response(404, NOT_FOUND, str(exc))
    if isinstance(exc, ConflictException):
        return _build_error_response(409, CONFLICT, str(exc))
    if isinstance(exc, ForbiddenException):
        return _build_error_response(403, FORBIDDEN, str(exc))
    if isinstance(exc, UnauthorizedException):
        return _build_error_response(401, UNAUTHORIZED, str(exc))
    if isinstance(exc, AuthServiceUnavailableException):
        return _build_error_response(503, AUTH_SERVICE_UNAVAILABLE, str(exc))
    return _build_error_response(500, INTERNAL_ERROR, str(exc))


async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    if exc.status_code == 401:
        return _build_error_response(401, UNAUTHORIZED, str(exc.detail))
    if exc.status_code == 403:
        return _build_error_response(403, FORBIDDEN, str(exc.detail))
    if exc.status_code == 404:
        return _build_error_response(404, NOT_FOUND, str(exc.detail))
    if exc.status_code == 400:
        return _build_error_response(400, VALIDATION_ERROR, str(exc.detail))
    return _build_error_response(exc.status_code, INTERNAL_ERROR, str(exc.detail))


async def validation_exception_handler(_: Request, exc: ValidationError) -> JSONResponse:
    return _build_error_response(422, VALIDATION_ERROR, str(exc))


async def request_validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return _build_error_response(422, VALIDATION_ERROR, str(exc))


async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    return _build_error_response(500, INTERNAL_ERROR, str(exc))


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DutyServiceException, duty_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
