class CoworkingException(Exception):
    def __init__(self, message: str, cause: Exception | None = None) -> None:
        super().__init__(message)
        self.cause = cause


class CoworkingNotFoundError(CoworkingException):
    def __init__(self, coworking_id: str | None = None, cause: Exception | None = None) -> None:
        msg = (
            f"Coworking with id {coworking_id} not found"
            if coworking_id
            else "Coworking not found"
        )
        super().__init__(msg, cause)


class BookingNotFoundError(CoworkingException):
    def __init__(self, booking_id: str | None = None, cause: Exception | None = None) -> None:
        msg = (
            f"Booking with id {booking_id} not found"
            if booking_id
            else "Booking not found"
        )
        super().__init__(msg, cause)


class CoworkingNotAvailableError(CoworkingException):
    def __init__(self, cause: Exception | None = None) -> None:
        super().__init__("Coworking is not available for booking", cause)


class BookingInvalidStatusTransitionError(CoworkingException):
    def __init__(
        self,
        current_status: str,
        target_action: str,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(
            f"Cannot {target_action} booking with status '{current_status}'",
            cause,
        )


class BookingAccessDeniedError(CoworkingException):
    def __init__(self, cause: Exception | None = None) -> None:
        super().__init__("You do not have permission to access this booking", cause)


class StudentAlreadyHasActiveBookingError(CoworkingException):
    def __init__(self, cause: Exception | None = None) -> None:
        super().__init__("Student already has an active or created booking", cause)
