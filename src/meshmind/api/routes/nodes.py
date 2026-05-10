from uuid import UUID

from fastapi import APIRouter, HTTPException

from meshmind.db.engine import AsyncSessionFactory
from meshmind.core.graph import KnowledgeGraph

router = APIRouter(prefix="/workspaces/{workspace_id}/nodes", tags=["nodes"])


@router.get("/{node_id}")
async def get_node(workspace_id: str, node_id: str):
    async with AsyncSessionFactory() as session:
        graph = KnowledgeGraph(session, UUID(workspace_id))
        node = await graph.get_node(UUID(node_id))
        if node is None:
            raise HTTPException(status_code=404, detail="Node not found")
        return node


@router.get("/{node_id}/related")
async def get_related(workspace_id: str, node_id: str):
    from meshmind.core.retrieval import KnowledgeRetrieval
    async with AsyncSessionFactory() as session:
        retrieval = KnowledgeRetrieval(session, UUID(workspace_id))
        related = await retrieval.get_related_nodes(UUID(node_id))
        return {"related": related}


@router.get("/{node_id}/documents")
async def get_node_documents(workspace_id: str, node_id: str):
    from meshmind.core.retrieval import KnowledgeRetrieval
    async with AsyncSessionFactory() as session:
        retrieval = KnowledgeRetrieval(session, UUID(workspace_id))
        docs = await retrieval.load_documents(UUID(node_id))
        return {"documents": docs}
