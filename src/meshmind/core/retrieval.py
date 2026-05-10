from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from meshmind.core.lifecycle import compute_current_vitality, is_below_threshold
from meshmind.db.repositories.documents import DocumentRepository
from meshmind.db.repositories.nodes import NodeRepository
from meshmind.db.repositories.relations import RelationRepository

VECTOR_WEIGHT = 0.7
BM25_WEIGHT = 0.3


class KnowledgeRetrieval:
    def __init__(self, session: AsyncSession, workspace_id: UUID):
        self.session = session
        self.workspace_id = workspace_id
        self.nodes = NodeRepository(session)
        self.documents = DocumentRepository(session)
        self.relations = RelationRepository(session)

    async def hybrid_search(
        self, query: str, embedding: list[float] | None = None, limit: int = 20,
    ) -> list[dict]:
        scores: dict[UUID, float] = {}
        node_map: dict[UUID, dict] = {}

        # Vector search
        if embedding is not None:
            vec_results = await self.nodes.search_by_embedding(
                embedding, self.workspace_id, limit=limit * 2
            )
            for node, similarity in vec_results:
                scores[node.node_id] = VECTOR_WEIGHT * similarity
                node_map[node.node_id] = self._node_to_dict(node)

        # BM25 search
        bm25_results = await self.nodes.search_by_text(
            query, self.workspace_id, limit=limit * 2
        )
        max_rank = max((getattr(n, "rank", 1) for n in bm25_results), default=1)
        for node in bm25_results:
            rank = getattr(node, "rank", 0)
            bm25_norm = rank / max_rank if max_rank > 0 else 0
            node_id = node.node_id
            scores[node_id] = scores.get(node_id, 0) + BM25_WEIGHT * bm25_norm
            if node_id not in node_map:
                node_map[node_id] = self._node_to_dict(node)

        # Filter by vitality threshold
        now = datetime.now(timezone.utc)
        filtered = []
        for node_id, score in scores.items():
            node_data = node_map[node_id]
            vitality = compute_current_vitality(
                node_data.get("vitality", 1.0),
                node_data.get("half_life_seconds", 0),
                node_data.get("created_at_dt", now),
                now,
            )
            if not is_below_threshold(vitality):
                node_data["computed_vitality"] = vitality
                node_data["score"] = score
                filtered.append(node_data)

        return sorted(filtered, key=lambda x: x["score"], reverse=True)[:limit]

    async def get_related_nodes(self, node_id: UUID) -> list[dict]:
        relations = await self.relations.find_by_source(node_id)
        related_ids = [r.target_node_id for r in relations]
        if not related_ids:
            return []
        nodes = await self.nodes.batch_get(related_ids)
        return [self._node_to_dict(n) for n in nodes if n.is_active]

    async def load_documents(self, node_id: UUID) -> list[dict]:
        docs = await self.documents.get_documents_for_node(node_id)
        return [
            {
                "document_id": str(d.document_id),
                "title": d.title,
                "s3_key": d.s3_key,
                "file_size": d.file_size,
                "file_type": d.file_type,
                "uploaded_by": d.uploaded_by,
                "created_at": d.created_at.isoformat() if d.created_at else None,
            }
            for d in docs
        ]

    def _node_to_dict(self, node) -> dict:
        hl = node.half_life
        hl_seconds = hl.total_seconds() if hasattr(hl, "total_seconds") else 0
        created = node.created_at
        if hasattr(created, "tzinfo") and created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        return {
            "node_id": str(node.node_id),
            "title": node.title,
            "summary": node.summary,
            "knowledge_type": node.knowledge_type,
            "vitality": node.vitality,
            "half_life_seconds": hl_seconds,
            "source_type": node.source_type,
            "user_id": node.user_id,
            "created_at_dt": created,
        }
