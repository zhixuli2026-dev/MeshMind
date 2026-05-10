from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from meshmind.db.models import WorkspaceModel
from meshmind.db.repositories.base import BaseRepository


class WorkspaceRepository(BaseRepository):
    model = WorkspaceModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_api_key_hash(self, key_hash: str) -> WorkspaceModel | None:
        result = await self.session.execute(
            select(WorkspaceModel).where(WorkspaceModel.api_key_hash == key_hash)
        )
        return result.scalar_one_or_none()
