from datetime import timedelta
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from meshmind.db.models import VitalityEventModel


class VitalityRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_latest_event(self, node_id: UUID) -> VitalityEventModel | None:
        result = await self.session.execute(
            select(VitalityEventModel)
            .where(VitalityEventModel.node_id == node_id)
            .order_by(VitalityEventModel.time.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def record_event(
        self, node_id: UUID, vitality: float, half_life: timedelta, event_type: str,
        context: dict | None = None,
    ) -> VitalityEventModel:
        event = VitalityEventModel(
            node_id=node_id,
            vitality=vitality,
            half_life=half_life,
            event_type=event_type,
            context=context or {},
        )
        self.session.add(event)
        await self.session.flush()
        return event
