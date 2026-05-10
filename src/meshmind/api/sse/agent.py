import json
import uuid
from uuid import UUID

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from meshmind.agents.main_agent import MainAgent
from meshmind.api.deps import get_harness
from meshmind.db.engine import AsyncSessionFactory
from meshmind.embedding.encoder import EmbeddingEncoder

router = APIRouter(prefix="/workspaces/{workspace_id}/sse", tags=["sse"])


@router.get("/agent/{conversation_id}")
async def agent_sse(workspace_id: str, conversation_id: str, q: str, request: Request):
    harness = get_harness()
    encoder: EmbeddingEncoder = request.app.state.encoder

    async def event_stream():
        yield {"event": "agent_start", "data": json.dumps({
            "conversation_id": conversation_id, "question": q,
        })}

        try:
            async with AsyncSessionFactory() as session:
                agent = MainAgent(harness, encoder, session, UUID(workspace_id))

                yield {"event": "main_agent_spawn", "data": json.dumps({
                    "parent_id": None,
                    "agent_id": f"ka-{uuid.uuid4().hex[:8]}",
                    "topic": q,
                })}

                result = await agent.ask(q)

                for i, source in enumerate(result.get("sources", []), 1):
                    yield {"event": "source_linked", "data": json.dumps({
                        "marker": f"N{i}",
                        "node_id": source.get("node_id"),
                        "title": source.get("title"),
                    })}

                yield {"event": "answer_chunk", "data": json.dumps({
                    "text": result.get("answer", ""),
                })}

                yield {"event": "answer_complete", "data": json.dumps({
                    "full_text": result.get("answer", ""),
                    "sources": [
                        {"N": i, "title": s.get("title"), "node_id": s.get("node_id")}
                        for i, s in enumerate(result.get("sources", []), 1)
                    ],
                })}

        except Exception as e:
            yield {"event": "error", "data": json.dumps({"message": str(e)})}

    return EventSourceResponse(event_stream())
