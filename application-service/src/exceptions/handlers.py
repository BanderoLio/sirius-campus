import structlog
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from src.constants.error_codes import (
    APP_ALREADY_DECIDED,
    APP_APPLICATION_NOT_FOUND,
    APP_DOCUMENT_NOT_FOUND,
    APP_FORBIDDEN,
    APP_INVALID_DOCUMENT_TYPE,
    APP_MINOR_VOICE_REQUIRED,
)
from src.domain.exceptions import (
    ApplicationAlreadyDecidedError,
    ApplicationException,
    ApplicationNotFoundError,
    DocumentNotFoundError,
    ForbiddenApplicationError,
    InvalidDocumentTypeError,
    MinorVoiceRequiredError,
)
from src.middleware.tracing import trace_id_var

logger = structlog.get_logger(__name__)


def _get_trace_id() -> str:
    try:
        return trace_id_var.get()
    except LookupError:
        return ""


def _map_exception_to_code(exc: ApplicationException) -> str:
    if isinstance(exc, ApplicationNotFoundError):
        return APP_APPLICATION_NOT_FOUND
    if isinstance(exc, DocumentNotFoundError):
        return APP_DOCUMENT_NOT_FOUND
    if isinstance(exc, InvalidDocumentTypeError):
        return APP_INVALID_DOCUMENT_TYPE
    if isinstance(exc, MinorVoiceRequiredError):
        return APP_MINOR_VOICE_REQUIRED
    if isinstance(exc, ForbiddenApplicationError):
        return APP_FORBIDDEN
    if isinstance(exc, ApplicationAlreadyDecidedError):
        return APP_ALREADY_DECIDED
    return "APP_UNKNOWN_ERROR"


def _get_status_code(exc: ApplicationException) -> int:
    if isinstance(exc, ApplicationNotFoundError):
        return status.HTTP_404_NOT_FOUND
    if isinstance(exc, DocumentNotFoundError):
        return status.HTTP_404_NOT_FOUND
    if isinstance(exc, ForbiddenApplicationError):
        return status.HTTP_403_FORBIDDEN
    if isinstance(exc, InvalidDocumentTypeError):
        return status.HTTP_400_BAD_REQUEST
    if isinstance(exc, MinorVoiceRequiredError):
        return status.HTTP_400_BAD_REQUEST
    if isinstance(exc, ApplicationAlreadyDecidedError):
        return status.HTTP_409_CONFLICT
    return status.HTTP_500_INTERNAL_SERVER_ERROR


async def application_exception_handler(
    request: Request,
    exc: ApplicationException,
) -> JSONResponse:
    code = _map_exception_to_code(exc)
    trace_id = _get_trace_id()
    logger.warning(
        "application_exception",
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
    app.add_exception_handler(ApplicationException, application_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
