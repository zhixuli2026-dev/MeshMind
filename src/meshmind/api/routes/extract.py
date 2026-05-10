import uuid
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from meshmind.api.deps import get_harness, get_storage
from meshmind.core.extraction import ExtractionPipeline
from meshmind.core.graph import KnowledgeGraph
from meshmind.db.engine import AsyncSessionFactory

router = APIRouter(prefix="/workspaces/{workspace_id}/extract", tags=["extract"])


class ConversationExtractRequest(BaseModel):
    messages: list[dict]
    user_id: str
    session_id: str


class DocumentExtractRequest(BaseModel):
    content: str
    title: str
    user_id: str


@router.post("/conversation")
async def extract_conversation(
    workspace_id: str,
    body: ConversationExtractRequest,
    request: Request,
):
    harness = get_harness()
    storage = get_storage()
    encoder = request.app.state.encoder
    pipeline = ExtractionPipeline(harness, encoder, storage)

    task_id = str(uuid.uuid4())

    async with AsyncSessionFactory() as session:
        graph = KnowledgeGraph(session, UUID(workspace_id))
        result = await pipeline.extract_from_conversation(
            messages=body.messages,
            graph=graph,
            user_id=body.user_id,
            session_id=body.session_id,
        )
        await session.commit()

    return {"task_id": task_id, "status": result.status, "created_nodes": result.created_nodes}


@router.post("/document")
async def extract_document(
    workspace_id: str,
    body: DocumentExtractRequest,
    request: Request,
):
    if len(body.content.encode("utf-8")) > 30 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Document exceeds 30MB limit")

    harness = get_harness()
    storage = get_storage()
    encoder = request.app.state.encoder
    pipeline = ExtractionPipeline(harness, encoder, storage)

    task_id = str(uuid.uuid4())

    async with AsyncSessionFactory() as session:
        graph = KnowledgeGraph(session, UUID(workspace_id))
        result = await pipeline.extract_from_document(
            content=body.content,
            title=body.title,
            graph=graph,
            user_id=body.user_id,
        )
        await session.commit()

    return {"task_id": task_id, "status": result.status, "created_nodes": result.created_nodes}
