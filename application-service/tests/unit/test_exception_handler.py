from src.constants.error_codes import (
    APP_APPLICATION_NOT_FOUND,
    APP_FORBIDDEN,
    APP_INVALID_DOCUMENT_TYPE,
)
from src.exceptions.handlers import _map_exception_to_code, _get_status_code
from src.domain.exceptions import (
    ApplicationNotFoundError,
    ForbiddenApplicationError,
    InvalidDocumentTypeError,
)


def test_map_application_not_found_to_code() -> None:
    exc = ApplicationNotFoundError(application_id="x")
    assert _map_exception_to_code(exc) == APP_APPLICATION_NOT_FOUND


def test_map_forbidden_to_code() -> None:
    exc = ForbiddenApplicationError()
    assert _map_exception_to_code(exc) == APP_FORBIDDEN


def test_map_invalid_document_type_to_code() -> None:
    exc = InvalidDocumentTypeError(document_type="x")
    assert _map_exception_to_code(exc) == APP_INVALID_DOCUMENT_TYPE


def test_status_code_not_found() -> None:
    exc = ApplicationNotFoundError()
    assert _get_status_code(exc) == 404


def test_status_code_forbidden() -> None:
    exc = ForbiddenApplicationError()
    assert _get_status_code(exc) == 403


def test_status_code_invalid_document() -> None:
    exc = InvalidDocumentTypeError()
    assert _get_status_code(exc) == 400
