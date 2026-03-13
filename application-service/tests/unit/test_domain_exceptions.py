import pytest

from src.domain.exceptions import (
    ApplicationNotFoundError,
    InvalidDocumentTypeError,
    MinorVoiceRequiredError,
    ForbiddenApplicationError,
    ApplicationAlreadyDecidedError,
)


def test_application_not_found_error_with_id() -> None:
    exc = ApplicationNotFoundError(application_id="123")
    assert "123" in str(exc)
    assert exc.cause is None


def test_application_not_found_error_without_id() -> None:
    exc = ApplicationNotFoundError()
    assert "not found" in str(exc).lower()


def test_invalid_document_type_error() -> None:
    exc = InvalidDocumentTypeError(document_type="invalid")
    assert "invalid" in str(exc)


def test_minor_voice_required_error() -> None:
    exc = MinorVoiceRequiredError()
    assert "voice" in str(exc).lower() or "minor" in str(exc).lower()


def test_forbidden_application_error() -> None:
    exc = ForbiddenApplicationError()
    assert "forbidden" in str(exc).lower() or "access" in str(exc).lower()


def test_application_already_decided_error() -> None:
    exc = ApplicationAlreadyDecidedError()
    assert "already" in str(exc).lower() or "approved" in str(exc).lower()
