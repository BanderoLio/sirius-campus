class DutyServiceException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class NotFoundException(DutyServiceException):
    pass


class ConflictException(DutyServiceException):
    pass


class UnauthorizedException(DutyServiceException):
    pass


class ForbiddenException(DutyServiceException):
    pass


class AuthServiceUnavailableException(DutyServiceException):
    pass
