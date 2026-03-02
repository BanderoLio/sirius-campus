import structlog
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from src.constants.error_codes import (
    PATROL_NOT_FOUND,
    PATROL_ENTRY_NOT_FOUND,
    PATROL_ALREADY_EXISTS,
    PATROL_ALREADY_COMPLETED,
    PATROL_NOT_IN_PROGRESS,
    VALIDATION_ERROR,
    UNAUTHORIZED,
    FORBIDDEN,
    INTERNAL_ERROR,
)
from src.domain.exceptions import (
    PatrolException,
    PatrolNotFoundError,
    PatrolEntryNotFoundError,
    PatrolAlreadyExistsError,
    PatrolAlreadyCompletedError,
    PatrolNotInProgressError,
    ValidationError,
    UnauthorizedError,
    ForbiddenError,
)
from src.middleware.tracing import trace_id_var

logger = structlog.get_logger(__name__)


def _get_trace_id() -> str:
    try:
        return trace_id_var.get()
    except LookupError:
        return ""


def _map_exception_to_code(exc: PatrolException) -> str:
    if isinstance(exc, PatrolNotFoundError):
        return PATROL_NOT_FOUND
    if isinstance(exc, PatrolEntryNotFoundError):
        return PATROL_ENTRY_NOT_FOUND
    if isinstance(exc, PatrolAlreadyExistsError):
        return PATROL_ALREADY_EXISTS
    if isinstance(exc, PatrolAlreadyCompletedError):
        return PATROL_ALREADY_COMPLETED
    if isinstance(exc, PatrolNotInProgressError):
        return PATROL_NOT_IN_PROGRESS
    if isinstance(exc, ValidationError):
        return VALIDATION_ERROR
    if isinstance(exc, UnauthorizedError):
        return UNAUTHORIZED
    if isinstance(exc, ForbiddenError):
        return FORBIDDEN
    return INTERNAL_ERROR


def _get_status_code(exc: PatrolException) -> int:
    if isinstance(exc, PatrolNotFoundError):
        return status.HTTP_404_NOT_FOUND
    if isinstance(exc, PatrolEntryNotFoundError):
        return status.HTTP_404_NOT_FOUND
    if isinstance(exc, PatrolAlreadyExistsError):
        return status.HTTP_409_CONFLICT
    if isinstance(exc, PatrolAlreadyCompletedError):
        return status.HTTP_422_UNPROCESSABLE_ENTITY
    if isinstance(exc, PatrolNotInProgressError):
        return status.HTTP_422_UNPROCESSABLE_ENTITY
    if isinstance(exc, ValidationError):
        return status.HTTP_400_BAD_REQUEST
    if isinstance(exc, UnauthorizedError):
        return status.HTTP_401_UNAUTHORIZED
    if isinstance(exc, ForbiddenError):
        return status.HTTP_403_FORBIDDEN
    return status.HTTP_500_INTERNAL_SERVER_ERROR


async def patrol_exception_handler(
    request: Request,
    exc: PatrolException,
) -> JSONResponse:
    code = _map_exception_to_code(exc)
    trace_id = _get_trace_id()
    logger.warning(
        "patrol_exception",
        code=code,
        message=str(exc),
        trace_id=trace_id,
    )
    return JSONResponse(
        status_code=_get_status_code(exc),
        content={
            "error": {
                "code": code,
                "message": str(exc),
                "trace_id": trace_id,
                "details": None,
            }
        },
    )


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    trace_id = _get_trace_id()
    code = "UNAUTHORIZED" if exc.status_code == 401 else "FORBIDDEN" if exc.status_code == 403 else "ERROR"
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": code,
                "message": exc.detail if isinstance(exc.detail, str) else str(exc.detail),
                "trace_id": trace_id,
                "details": None,
            }
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(PatrolException, patrol_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
