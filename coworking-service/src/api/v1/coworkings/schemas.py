from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CoworkingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    building: int
    entrance: int
    number: int
    available: bool
