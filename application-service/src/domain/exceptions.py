class ApplicationException(Exception):
    def __init__(self, message: str, cause: Exception | None = None) -> None:
        super().__init__(message)
        self.cause = cause


class ApplicationNotFoundError(ApplicationException):
    def __init__(self, application_id: str | None = None, cause: Exception | None = None) -> None:
        msg = f"Application with id {application_id} not found" if application_id else "Application not found"
        super().__init__(msg, cause)


class DocumentNotFoundError(ApplicationException):
    def __init__(self, document_id: str | None = None, cause: Exception | None = None) -> None:
        msg = f"Document with id {document_id} not found" if document_id else "Document not found"
        super().__init__(msg, cause)


class InvalidDocumentTypeError(ApplicationException):
    def __init__(self, document_type: str | None = None, cause: Exception | None = None) -> None:
        msg = f"Invalid document type: {document_type}" if document_type else "Invalid document type"
        super().__init__(msg, cause)


class MinorVoiceRequiredError(ApplicationException):
    def __init__(self, cause: Exception | None = None) -> None:
        super().__init__(
            "For minors, a parent voice message (voice_message) is required",
            cause,
        )


class ForbiddenApplicationError(ApplicationException):
    def __init__(self, cause: Exception | None = None) -> None:
        super().__init__("Access to this application is forbidden", cause)


class ApplicationAlreadyDecidedError(ApplicationException):
    def __init__(self, cause: Exception | None = None) -> None:
        super().__init__("Application has already been approved or rejected", cause)
