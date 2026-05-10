from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from meshmind.db.models import AuthorModel, KnowledgeNodeModel
from meshmind.db.repositories.base import BaseRepository


class NodeRepository(BaseRepository):
    model = KnowledgeNodeModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def find_by_workspace(
        self, workspace_id: UUID, *, is_active: bool = True, limit: int = 100
    ) -> list[KnowledgeNodeModel]:
        result = await self.session.execute(
            select(KnowledgeNodeModel)
            .where(
                KnowledgeNodeModel.workspace_id == workspace_id,
                KnowledgeNodeModel.is_active == is_active,
            )
            .limit(limit)
        )
        return list(result.scalars().all())

    async def search_by_embedding(
        self, embedding: list[float], workspace_id: UUID, limit: int = 20
    ) -> list[tuple[KnowledgeNodeModel, float]]:
        query = text("""
            SELECT n.*, 1 - (embedding <=> :emb) AS similarity
            FROM meshmind.knowledge_nodes n
            WHERE n.workspace_id = :ws_id AND n.is_active = TRUE
            ORDER BY embedding <=> :emb
            LIMIT :lim
        """)
        result = await self.session.execute(query, {
            "emb": embedding,
            "ws_id": workspace_id,
            "lim": limit,
        })
        rows = result.fetchall()
        nodes = []
        for row in rows:
            node = KnowledgeNodeModel(
                node_id=row[0], workspace_id=row[1], title=row[2],
                summary=row[3], knowledge_type=row[4], vitality=row[5],
                half_life=row[6], is_active=row[7], source_type=row[9],
                user_id=row[10], session_id=row[11], agent_id=row[12],
                created_at=row[13], updated_at=row[14],
            )
            nodes.append((node, float(row[15])))
        return nodes

    async def search_by_text(
        self, query: str, workspace_id: UUID, limit: int = 20
    ) -> list[KnowledgeNodeModel]:
        ts_query = " | ".join(query.split())
        sql = text("""
            SELECT n.*, ts_rank(to_tsvector('simple', n.title || ' ' || n.summary), to_tsquery('simple', :q)) AS rank
            FROM meshmind.knowledge_nodes n
            WHERE n.workspace_id = :ws_id AND n.is_active = TRUE
              AND to_tsvector('simple', n.title || ' ' || n.summary) @@ to_tsquery('simple', :q)
            ORDER BY rank DESC
            LIMIT :lim
        """)
        result = await self.session.execute(sql, {"q": ts_query, "ws_id": workspace_id, "lim": limit})
        rows = result.fetchall()
        return [
            KnowledgeNodeModel(
                node_id=r[0], workspace_id=r[1], title=r[2], summary=r[3],
                knowledge_type=r[4], vitality=r[5], half_life=r[6],
                is_active=r[7], source_type=r[9], user_id=r[10],
                session_id=r[11], agent_id=r[12], created_at=r[13], updated_at=r[14],
            )
            for r in rows
        ]

    async def get_authors(self, node_id: UUID) -> list[AuthorModel]:
        from meshmind.db.models import NodeAuthorModel
        result = await self.session.execute(
            select(AuthorModel)
            .join(NodeAuthorModel, NodeAuthorModel.author_id == AuthorModel.author_id)
            .where(NodeAuthorModel.node_id == node_id)
        )
        return list(result.scalars().all())

    async def batch_get(self, node_ids: list[UUID]) -> list[KnowledgeNodeModel]:
        result = await self.session.execute(
            select(KnowledgeNodeModel).where(KnowledgeNodeModel.node_id.in_(node_ids))
        )
        return list(result.scalars().all())
