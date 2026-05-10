from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from meshmind.core.lifecycle import get_initial_half_life, get_initial_vitality
from meshmind.db.repositories.authors import AuthorRepository
from meshmind.db.repositories.nodes import NodeRepository
from meshmind.db.repositories.relations import RelationRepository
from meshmind.db.repositories.vitality import VitalityRepository


class KnowledgeGraph:
    def __init__(self, session: AsyncSession, workspace_id: UUID):
        self.session = session
        self.workspace_id = workspace_id
        self.nodes = NodeRepository(session)
        self.relations = RelationRepository(session)
        self.authors = AuthorRepository(session)
        self.vitality = VitalityRepository(session)

    async def create_node(
        self,
        title: str,
        summary: str,
        knowledge_type: str,
        source_type: str,
        *,
        user_id: str | None = None,
        session_id: str | None = None,
        agent_id: str | None = None,
        embedding: list[float] | None = None,
    ) -> UUID:
        half_life = get_initial_half_life(knowledge_type)
        vitality_value = get_initial_vitality(source_type)

        node = await self.nodes.create(
            workspace_id=self.workspace_id,
            title=title,
            summary=summary,
            knowledge_type=knowledge_type,
            vitality=vitality_value,
            half_life=half_life,
            source_type=source_type,
            user_id=user_id or "unknown",
            session_id=session_id,
            agent_id=agent_id,
            embedding=embedding,
        )

        await self.vitality.record_event(
            node_id=node.node_id,
            vitality=vitality_value,
            half_life=half_life,
            event_type="created",
        )

        if user_id and user_id != "unknown":
            author = await self.authors.get_or_create(self.workspace_id, user_id)
            from meshmind.db.models import NodeAuthorModel
            self.session.add(NodeAuthorModel(node_id=node.node_id, author_id=author.author_id))
            await self.session.flush()

        return node.node_id

    async def update_node(self, node_id: UUID, **kwargs) -> None:
        node = await self.nodes.get_by_id(node_id)
        if node is None:
            raise ValueError(f"Node {node_id} not found")
        await self.nodes.update(node, **kwargs)

    async def delete_node(self, node_id: UUID) -> None:
        node = await self.nodes.get_by_id(node_id)
        if node is None:
            raise ValueError(f"Node {node_id} not found")
        await self.nodes.update(node, is_active=False)

    async def create_relation(
        self, source_id: UUID, target_id: UUID, relation_type: str
    ) -> UUID:
        existing = await self.relations.find_between(source_id, target_id)
        if existing and existing.relation_type == relation_type:
            return existing.relationship_id
        rel = await self.relations.create(
            workspace_id=self.workspace_id,
            source_node_id=source_id,
            target_node_id=target_id,
            relation_type=relation_type,
        )
        return rel.relationship_id

    async def delete_relation(self, relation_id: UUID) -> None:
        rel = await self.relations.get_by_id(relation_id)
        if rel:
            await self.relations.delete(rel)

    async def get_node(self, node_id: UUID) -> dict | None:
        node = await self.nodes.get_by_id(node_id)
        if node is None:
            return None
        authors = await self.nodes.get_authors(node_id)
        relations = await self.relations.find_by_source(node_id)
        return {
            "node_id": str(node.node_id),
            "title": node.title,
            "summary": node.summary,
            "knowledge_type": node.knowledge_type,
            "vitality": node.vitality,
            "half_life": str(node.half_life),
            "is_active": node.is_active,
            "source_type": node.source_type,
            "user_id": node.user_id,
            "session_id": node.session_id,
            "created_at": node.created_at.isoformat() if node.created_at else None,
            "authors": [{"user_id": a.user_id, "name": a.name} for a in authors],
            "relations": [
                {"target": str(r.target_node_id), "type": r.relation_type}
                for r in relations
            ],
        }

    async def get_conflicts(self) -> list[dict]:
        conflicts = await self.relations.find_conflicts(self.workspace_id)
        return [
            {
                "source": str(c.source_node_id),
                "target": str(c.target_node_id),
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in conflicts
        ]
