from src.database.models import DutyCategory
from src.repositories.duty_category_repository import DutyCategoryRepository


class DutyCategoryService:
    def __init__(self, repository: DutyCategoryRepository) -> None:
        self.repository = repository

    async def list(self, page: int, size: int) -> tuple[list[DutyCategory], int]:
        return await self.repository.list(page=page, size=size)
