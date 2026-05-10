from uuid import UUID

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from meshmind.db.models import RelationModel
from meshmind.db.repositories.base import BaseRepository


class RelationRepository(BaseRepository):
    model = RelationModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def find_by_source(self, node_id: UUID) -> list[RelationModel]:
        result = await self.session.execute(
            select(RelationModel).where(RelationModel.source_node_id == node_id)
        )
        return list(result.scalars().all())

    async def find_by_target(self, node_id: UUID) -> list[RelationModel]:
        result = await self.session.execute(
            select(RelationModel).where(RelationModel.target_node_id == node_id)
        )
        return list(result.scalars().all())

    async def find_between(self, node_a: UUID, node_b: UUID) -> RelationModel | None:
        result = await self.session.execute(
            select(RelationModel).where(
                or_(
                    (RelationModel.source_node_id == node_a) & (RelationModel.target_node_id == node_b),
                    (RelationModel.source_node_id == node_b) & (RelationModel.target_node_id == node_a),
                )
            )
        )
        return result.scalar_one_or_none()

    async def find_conflicts(self, workspace_id: UUID) -> list[RelationModel]:
        result = await self.session.execute(
            select(RelationModel).where(
                RelationModel.workspace_id == workspace_id,
                RelationModel.relation_type == "conflict",
            )
        )
        return list(result.scalars().all())
