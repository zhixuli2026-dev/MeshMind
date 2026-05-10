from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from meshmind.db.models import DocumentModel
from meshmind.db.repositories.base import BaseRepository


class DocumentRepository(BaseRepository):
    model = DocumentModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def find_by_workspace(self, workspace_id: UUID) -> list[DocumentModel]:
        result = await self.session.execute(
            select(DocumentModel).where(DocumentModel.workspace_id == workspace_id)
        )
        return list(result.scalars().all())

    async def get_documents_for_node(self, node_id: UUID) -> list[DocumentModel]:
        from meshmind.db.models import NodeDocumentModel
        result = await self.session.execute(
            select(DocumentModel)
            .join(NodeDocumentModel, NodeDocumentModel.document_id == DocumentModel.document_id)
            .where(NodeDocumentModel.node_id == node_id)
        )
        return list(result.scalars().all())
