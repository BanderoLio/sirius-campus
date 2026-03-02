class PatrolException(Exception):
    def __init__(self, message: str, cause: Exception | None = None) -> None:
        super().__init__(message)
        self.cause = cause


class PatrolNotFoundError(PatrolException):
    def __init__(self, patrol_id: str | None = None, cause: Exception | None = None) -> None:
        msg = f"Обход с ID {patrol_id} не найден" if patrol_id else "Обход не найден"
        super().__init__(msg, cause)


class PatrolEntryNotFoundError(PatrolException):
    def __init__(self, patrol_entry_id: str | None = None, cause: Exception | None = None) -> None:
        msg = f"Запись проверки с ID {patrol_entry_id} не найдена" if patrol_entry_id else "Запись проверки не найдена"
        super().__init__(msg, cause)


class PatrolAlreadyExistsError(PatrolException):
    def __init__(self, building: str, entrance: int, date: str, cause: Exception | None = None) -> None:
        msg = f"Обход для корпуса {building}, подъезда {entrance} на дату {date} уже существует"
        super().__init__(msg, cause)


class PatrolAlreadyCompletedError(PatrolException):
    def __init__(self, cause: Exception | None = None) -> None:
        super().__init__("Обход уже завершён, повторное завершение невозможно", cause)


class PatrolNotInProgressError(PatrolException):
    def __init__(self, cause: Exception | None = None) -> None:
        super().__init__("Обход не в статусе in_progress, обновление невозможно", cause)


class ValidationError(PatrolException):
    """Raised when request data fails business validation."""

    def __init__(self, message: str, cause: Exception | None = None) -> None:
        super().__init__(message, cause)


class UnauthorizedError(PatrolException):
    def __init__(self, message: str = "Токен отсутствует или невалиден", cause: Exception | None = None) -> None:
        super().__init__(message, cause)


class ForbiddenError(PatrolException):
    def __init__(self, message: str = "Недостаточно прав", cause: Exception | None = None) -> None:
        super().__init__(message, cause)
