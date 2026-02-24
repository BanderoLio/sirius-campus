from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass
class LeaveRecord:
    user_id: str
    user_name: str
    room: str
    leave_time: datetime
    return_time: datetime
    reason: str


class ApplicationClientProtocol(Protocol):
    async def get_approved_leaves(
        self,
        *,
        date: str,
        building: str,
        entrance: int,
    ) -> list[LeaveRecord]:
        ...


class ApplicationClientStub:
    """Stub for development when application-service is not available."""

    async def get_approved_leaves(
        self,
        *,
        date: str,
        building: str,
        entrance: int,
    ) -> list[LeaveRecord]:
        # Stub returns test approved leaves for the specified date and entrance
        from datetime import timezone
        
        if building == "8" and entrance == 1:
            return [
                LeaveRecord(
                    user_id="00000000-0000-0000-0000-000000000002",
                    user_name="Петров Петр Петрович",
                    room="201",
                    leave_time=datetime(2025, 1, 15, 10, 0, tzinfo=timezone.utc),
                    return_time=datetime(2025, 1, 15, 18, 0, tzinfo=timezone.utc),
                    reason="Поездка в город",
                ),
            ]
        return []


def get_application_client() -> ApplicationClientProtocol:
    return ApplicationClientStub()
