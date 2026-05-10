from uuid import UUID

from fastapi import APIRouter, Query, Request

router = APIRouter(prefix="/workspaces/{workspace_id}/search", tags=["search"])


@router.get("")
async def search_knowledge(
    workspace_id: str,
    q: str = Query(..., description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    request: Request = None,
):
    from meshmind.core.retrieval import KnowledgeRetrieval
    from meshmind.db.engine import AsyncSessionFactory

    ws_uuid = UUID(workspace_id)
    encoder = request.app.state.encoder
    embedding = encoder.encode_single(q)

    async with AsyncSessionFactory() as session:
        retrieval = KnowledgeRetrieval(session, ws_uuid)
        results = await retrieval.hybrid_search(q, embedding=embedding, limit=limit)

    return {"results": results, "count": len(results)}
