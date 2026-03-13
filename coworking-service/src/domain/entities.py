from datetime import datetime
from uuid import UUID


class Coworking:
    def __init__(
        self,
        id: UUID,
        name: str,
        building: int,
        entrance: int,
        number: int,
        available: bool,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        self.id = id
        self.name = name
        self.building = building
        self.entrance = entrance
        self.number = number
        self.available = available
        self.created_at = created_at
        self.updated_at = updated_at


class CoworkingBooking:
    def __init__(
        self,
        id: UUID,
        student_id: UUID,
        coworking_id: UUID,
        taken_from: datetime,
        returned_back: datetime,
        status: str,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        self.id = id
        self.student_id = student_id
        self.coworking_id = coworking_id
        self.taken_from = taken_from
        self.returned_back = returned_back
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
