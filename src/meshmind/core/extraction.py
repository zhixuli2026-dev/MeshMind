import json
import uuid
from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel

from meshmind.core.config import settings
from meshmind.core.graph import KnowledgeGraph
from meshmind.embedding.encoder import EmbeddingEncoder
from meshmind.llm.harness import LLMHarness, TaskType
from meshmind.llm.prompts import (
    EXTRACT_FROM_CONVERSATION,
    EXTRACT_FROM_DOCUMENT_DECISION,
    EXTRACT_FROM_DOCUMENT_SPLIT,
    EXTRACT_FROM_DOCUMENT_WHOLE,
    GRAPH_CONNECT_JUDGMENT,
)
from meshmind.storage.s3 import StorageClient


class KnowledgeItem(BaseModel):
    title: str
    summary: str
    type: str  # law/rule/best_practice/event


class ExtractionResult:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.status: str = "pending"
        self.created_nodes: list[str] = []
        self.updated_nodes: list[str] = []
        self.conflicts: list[tuple[str, str]] = []


class GraphConnectJudgment(BaseModel):
    decision: str  # duplicate/similar/conflict/related/unrelated
    relation_type: str | None = None
    reasoning: str = ""


class ExtractionPipeline:
    def __init__(
        self,
        harness: LLMHarness,
        encoder: EmbeddingEncoder,
        storage: StorageClient,
    ):
        self.harness = harness
        self.encoder = encoder
        self.storage = storage

    async def extract_from_conversation(
        self,
        messages: list[dict],
        graph: KnowledgeGraph,
        *,
        user_id: str,
        session_id: str,
    ) -> ExtractionResult:
        task_id = str(uuid.uuid4())
        result = ExtractionResult(task_id)

        # Step 1: LLM extraction
        conversation_text = "\n".join(
            f"{m['role']}: {m['content']}" for m in messages
        )
        prompt = EXTRACT_FROM_CONVERSATION.format(conversation_text=conversation_text)
        items_json = await self.harness.call(
            messages=[{"role": "user", "content": prompt}],
            task=TaskType.CONVERSATION_EXTRACTION,
            max_tokens=4096,
            temperature=0.3,
            use_json=True,
        )

        try:
            data = json.loads(items_json.content)
            if isinstance(data, dict):
                data = data.get("items", data.get("knowledge_points", []))
            if not isinstance(data, list):
                data = []
        except json.JSONDecodeError:
            data = []

        # Step 2: For each item, find connections and write
        for item_data in data:
            try:
                item = KnowledgeItem(**item_data)
            except Exception:
                continue

            embedding = self.encoder.encode_single(f"{item.title}\n{item.summary}")
            node_id = await self._add_with_connections(
                graph=graph,
                title=item.title,
                summary=item.summary,
                knowledge_type=item.type,
                source_type="conversation",
                user_id=user_id,
                session_id=session_id,
                embedding=embedding,
            )

            if node_id:
                result.created_nodes.append(str(node_id))

        result.status = "done"
        return result

    async def extract_from_document(
        self,
        content: str,
        title: str,
        graph: KnowledgeGraph,
        *,
        user_id: str,
    ) -> ExtractionResult:
        task_id = str(uuid.uuid4())
        result = ExtractionResult(task_id)

        # Store document in MinIO
        s3_key = f"{graph.workspace_id}/{task_id}/{title}.md"
        file_size = len(content.encode("utf-8"))
        await self.storage.upload(s3_key, content)

        from meshmind.db.repositories.documents import DocumentRepository
        doc_repo = DocumentRepository(graph.session)
        doc = await doc_repo.create(
            workspace_id=graph.workspace_id,
            title=title,
            s3_key=s3_key,
            file_size=file_size,
            uploaded_by=user_id,
            content_text=content[:100000],
        )

        # Step 1: LLM decides whole vs split
        decision_prompt = EXTRACT_FROM_DOCUMENT_DECISION.format(
            title=title, content_preview=content[:3000]
        )
        decision_resp = await self.harness.call_structured(
            messages=[{"role": "user", "content": decision_prompt}],
            task=TaskType.DOCUMENT_ANALYSIS,
            output_model=GraphConnectJudgment,
        )

        # Step 2: Extract based on strategy
        if decision_resp.decision == "whole" or decision_resp.decision == "whole":
            items = await self._extract_whole_document(content, title)
        else:
            items = await self._extract_split_document(content, title)

        # Step 3: Add to graph with connections
        for item in items:
            embedding = self.encoder.encode_single(f"{item.title}\n{item.summary}")
            node_id = await self._add_with_connections(
                graph=graph,
                title=item.title,
                summary=item.summary,
                knowledge_type=item.type,
                source_type="document",
                user_id=user_id,
                embedding=embedding,
            )

            if node_id:
                result.created_nodes.append(str(node_id))
                # Link node to document
                from meshmind.db.models import NodeDocumentModel
                graph.session.add(
                    NodeDocumentModel(node_id=node_id, document_id=doc.document_id)
                )
                await graph.session.flush()

        result.status = "done"
        return result

    async def _add_with_connections(
        self,
        graph: KnowledgeGraph,
        title: str,
        summary: str,
        knowledge_type: str,
        source_type: str,
        user_id: str,
        embedding: list[float],
        session_id: str | None = None,
    ) -> UUID | None:
        # Search for candidates
        candidates = await graph.nodes.search_by_embedding(
            embedding, graph.workspace_id, limit=20
        )

        # LLM judges each candidate
        for cand_node, _ in candidates[:10]:
            judgment = await self._judge_connection(
                new_title=title,
                new_summary=summary,
                new_type=knowledge_type,
                existing_title=cand_node.title,
                existing_summary=cand_node.summary,
                existing_type=cand_node.knowledge_type,
            )

            if judgment.decision == "duplicate":
                return None  # Don't add
            elif judgment.decision == "similar":
                # Update existing
                await graph.nodes.update(
                    cand_node,
                    summary=f"{cand_node.summary}\n{summary}",
                    updated_at=datetime.now(timezone.utc),
                )
                if user_id and user_id != "unknown":
                    author_repo = graph.authors
                    author = await author_repo.get_or_create(graph.workspace_id, user_id)
                    from meshmind.db.models import NodeAuthorModel
                    graph.session.add(
                        NodeAuthorModel(node_id=cand_node.node_id, author_id=author.author_id)
                    )
                    await graph.session.flush()
                return cand_node.node_id
            elif judgment.decision == "conflict":
                node_id = await graph.create_node(
                    title=title, summary=summary,
                    knowledge_type=knowledge_type, source_type=source_type,
                    user_id=user_id, session_id=session_id,
                    embedding=embedding,
                )
                await graph.create_relation(cand_node.node_id, node_id, "conflict")
                return node_id
            elif judgment.decision == "related" and judgment.relation_type:
                node_id = await graph.create_node(
                    title=title, summary=summary,
                    knowledge_type=knowledge_type, source_type=source_type,
                    user_id=user_id, session_id=session_id,
                    embedding=embedding,
                )
                await graph.create_relation(
                    cand_node.node_id if judgment.relation_type != "derived_from" else node_id,
                    node_id if judgment.relation_type != "derived_from" else cand_node.node_id,
                    judgment.relation_type,
                )
                return node_id

        # No match found → create standalone
        return await graph.create_node(
            title=title, summary=summary,
            knowledge_type=knowledge_type, source_type=source_type,
            user_id=user_id, session_id=session_id,
            embedding=embedding,
        )

    async def _judge_connection(
        self, new_title, new_summary, new_type,
        existing_title, existing_summary, existing_type,
    ) -> GraphConnectJudgment:
        prompt = GRAPH_CONNECT_JUDGMENT.format(
            new_title=new_title, new_summary=new_summary, new_type=new_type,
            existing_title=existing_title, existing_summary=existing_summary,
            existing_type=existing_type,
        )
        return await self.harness.call_structured(
            messages=[{"role": "user", "content": prompt}],
            task=TaskType.MAINTENANCE_JUDGMENT,
            output_model=GraphConnectJudgment,
        )

    async def _extract_whole_document(self, content: str, title: str) -> list[KnowledgeItem]:
        prompt = EXTRACT_FROM_DOCUMENT_WHOLE.format(title=title, content=content[:8000])
        resp = await self.harness.call(
            messages=[{"role": "user", "content": prompt}],
            task=TaskType.DOCUMENT_ANALYSIS,
            max_tokens=2048,
            use_json=True,
        )
        try:
            data = json.loads(resp.content)
            return [KnowledgeItem(**data)]
        except Exception:
            return []

    async def _extract_split_document(self, content: str, title: str) -> list[KnowledgeItem]:
        prompt = EXTRACT_FROM_DOCUMENT_SPLIT.format(title=title, content=content[:8000])
        resp = await self.harness.call(
            messages=[{"role": "user", "content": prompt}],
            task=TaskType.DOCUMENT_ANALYSIS,
            max_tokens=4096,
            use_json=True,
        )
        try:
            data = json.loads(resp.content)
            if isinstance(data, dict):
                data = data.get("items", data.get("knowledge_points", []))
            return [KnowledgeItem(**item) for item in data if isinstance(item, dict)]
        except Exception:
            return []
