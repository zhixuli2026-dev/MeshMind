from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from meshmind.db.models import AuthorModel, NodeAuthorModel
from meshmind.db.repositories.base import BaseRepository


class AuthorRepository(BaseRepository):
    model = AuthorModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_or_create(
        self, workspace_id: UUID, user_id: str, name: str | None = None
    ) -> AuthorModel:
        result = await self.session.execute(
            select(AuthorModel).where(
                AuthorModel.workspace_id == workspace_id,
                AuthorModel.user_id == user_id,
            )
        )
        author = result.scalar_one_or_none()
        if author is None:
            author = AuthorModel(workspace_id=workspace_id, user_id=user_id, name=name)
            self.session.add(author)
            await self.session.flush()
        elif name and author.name != name:
            author.name = name
            await self.session.flush()
        return author

    async def get_authors_for_node(self, node_id: UUID) -> list[AuthorModel]:
        result = await self.session.execute(
            select(AuthorModel)
            .join(NodeAuthorModel, NodeAuthorModel.author_id == AuthorModel.author_id)
            .where(NodeAuthorModel.node_id == node_id)
        )
        return list(result.scalars().all())
