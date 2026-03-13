from datetime import date, datetime
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.application import ApplicationModel


class ApplicationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, application_id: UUID) -> ApplicationModel | None:
        result = await self._session.execute(
            select(ApplicationModel).where(ApplicationModel.id == application_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_documents(
        self, application_id: UUID
    ) -> ApplicationModel | None:
        result = await self._session.execute(
            select(ApplicationModel)
            .where(ApplicationModel.id == application_id)
            .options(selectinload(ApplicationModel.documents))
        )
        return result.scalar_one_or_none()

    async def get_list(
        self,
        *,
        user_id: UUID | None = None,
        user_ids: list[UUID] | None = None,
        status: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[ApplicationModel], int]:
        if user_ids is not None and len(user_ids) == 0:
            return [], 0
        q = select(ApplicationModel)
        count_q = select(func.count()).select_from(ApplicationModel)
        conditions = []
        if user_id is not None:
            conditions.append(ApplicationModel.user_id == user_id)
        if user_ids is not None:
            conditions.append(ApplicationModel.user_id.in_(user_ids))
        if status is not None:
            conditions.append(ApplicationModel.status == status)
        if date_from is not None:
            conditions.append(func.date(ApplicationModel.leave_time) >= date_from)
        if date_to is not None:
            conditions.append(func.date(ApplicationModel.leave_time) <= date_to)
        if conditions:
            q = q.where(and_(*conditions))
            count_q = count_q.where(and_(*conditions))
        total_result = await self._session.execute(count_q)
        total = total_result.scalar() or 0
        q = q.order_by(ApplicationModel.created_at.desc()).offset((page - 1) * size).limit(size)
        result = await self._session.execute(q)
        rows = list(result.scalars().all())
        return rows, total

    async def get_approved_for_leave_date(
        self,
        leave_date: date,
        building: str | None = None,
    ) -> list[ApplicationModel]:
        start = datetime.combine(leave_date, datetime.min.time())
        end = datetime.combine(leave_date, datetime.max.time())
        q = select(ApplicationModel).where(
            and_(
                ApplicationModel.status == "approved",
                ApplicationModel.leave_time >= start,
                ApplicationModel.leave_time <= end,
            )
        )
        result = await self._session.execute(q)
        return list(result.scalars().all())

    async def create(
        self,
        user_id: UUID,
        is_minor: bool,
        leave_time: datetime,
        return_time: datetime,
        reason: str,
        contact_phone: str,
    ) -> ApplicationModel:
        model = ApplicationModel(
            user_id=user_id,
            is_minor=is_minor,
            leave_time=leave_time,
            return_time=return_time,
            reason=reason,
            contact_phone=contact_phone,
            status="pending",
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return model

    async def update_status(
        self,
        application_id: UUID,
        status: str,
        decided_by: UUID,
        decided_at: datetime,
        reject_reason: str | None = None,
    ) -> ApplicationModel | None:
        model = await self.get_by_id(application_id)
        if model is None:
            return None
        model.status = status
        model.decided_by = decided_by
        model.decided_at = decided_at
        model.reject_reason = reject_reason
        await self._session.flush()
        await self._session.refresh(model)
        return model
