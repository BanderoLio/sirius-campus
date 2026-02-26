import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from src.constants.error_codes import (
    BOOKING_ACCESS_DENIED,
    BOOKING_INVALID_STATUS_TRANSITION,
    BOOKING_NOT_FOUND,
    COWORKING_NOT_AVAILABLE,
    COWORKING_NOT_FOUND,
    STUDENT_ALREADY_HAS_ACTIVE_BOOKING,
)
from src.domain.exceptions import (
    BookingAccessDeniedError,
    BookingInvalidStatusTransitionError,
    BookingNotFoundError,
    CoworkingException,
    CoworkingNotAvailableError,
    CoworkingNotFoundError,
    StudentAlreadyHasActiveBookingError,
)
from src.middleware.tracing import trace_id_var

logger = structlog.get_logger(__name__)


def _get_trace_id() -> str:
    try:
        return trace_id_var.get()
    except LookupError:
        return ""


def _map_exception_to_code(exc: CoworkingException) -> str:
    if isinstance(exc, CoworkingNotFoundError):
        return COWORKING_NOT_FOUND
    if isinstance(exc, BookingNotFoundError):
        return BOOKING_NOT_FOUND
    if isinstance(exc, CoworkingNotAvailableError):
        return COWORKING_NOT_AVAILABLE
    if isinstance(exc, BookingInvalidStatusTransitionError):
        return BOOKING_INVALID_STATUS_TRANSITION
    if isinstance(exc, BookingAccessDeniedError):
        return BOOKING_ACCESS_DENIED
    if isinstance(exc, StudentAlreadyHasActiveBookingError):
        return STUDENT_ALREADY_HAS_ACTIVE_BOOKING
    return "COWORKING_UNKNOWN_ERROR"


def _get_status_code(exc: CoworkingException) -> int:
    if isinstance(exc, CoworkingNotFoundError):
        return status.HTTP_404_NOT_FOUND
    if isinstance(exc, BookingNotFoundError):
        return status.HTTP_404_NOT_FOUND
    if isinstance(exc, CoworkingNotAvailableError):
        return status.HTTP_409_CONFLICT
    if isinstance(exc, BookingInvalidStatusTransitionError):
        return status.HTTP_409_CONFLICT
    if isinstance(exc, BookingAccessDeniedError):
        return status.HTTP_403_FORBIDDEN
    if isinstance(exc, StudentAlreadyHasActiveBookingError):
        return status.HTTP_409_CONFLICT
    return status.HTTP_500_INTERNAL_SERVER_ERROR


async def coworking_exception_handler(
    request: Request,
    exc: CoworkingException,
) -> JSONResponse:
    code = _map_exception_to_code(exc)
    trace_id = _get_trace_id()
    logger.warning(
        "coworking_exception",
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
    code = (
        "UNAUTHORIZED"
        if exc.status_code == 401
        else "FORBIDDEN"
        if exc.status_code == 403
        else "ERROR"
    )
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
    app.add_exception_handler(CoworkingException, coworking_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore[arg-type]
