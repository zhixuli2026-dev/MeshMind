import json
import uuid
from uuid import UUID

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from meshmind.agents.knowledge_agent import create_knowledge_agent
from meshmind.api.deps import get_harness
from meshmind.core.maintenance import MaintenanceService
from meshmind.core.retrieval import KnowledgeRetrieval
from meshmind.db.engine import AsyncSessionFactory
from meshmind.embedding.encoder import EmbeddingEncoder

router = APIRouter(prefix="/workspaces/{workspace_id}/sse", tags=["sse"])


@router.get("/agent/{conversation_id}")
async def agent_sse(workspace_id: str, conversation_id: str, q: str, request: Request):
    harness = get_harness()
    encoder: EmbeddingEncoder = request.app.state.encoder

    async def event_stream():
        conv_id = conversation_id
        yield {"event": "agent_start", "data": json.dumps({
            "conversation_id": conv_id, "question": q,
        })}

        agent_id = f"ka-{uuid.uuid4().hex[:8]}"
        yield {"event": "main_agent_spawn", "data": json.dumps({
            "parent_id": None, "agent_id": agent_id, "topic": q,
        })}

        try:
            async with AsyncSessionFactory() as session:
                retrieval = KnowledgeRetrieval(session, UUID(workspace_id))
                agent = create_knowledge_agent(harness, retrieval, encoder, agent_id)

                initial_state = {
                    "question": q,
                    "workspace_id": workspace_id,
                    "loaded_knowledge": [],
                    "missing": [],
                    "enough": False,
                }

                final_state = None
                async for chunk in agent.astream(initial_state):
                    final_state = chunk
                    # Stream intermediate states as events
                    for _node_name, node_state in chunk.items():
                        if node_state.get("current_thought"):
                            try:
                                thought_data = json.loads(node_state["current_thought"])
                            except Exception:
                                thought_data = {}
                            yield {"event": "think", "data": json.dumps({
                                "agent_id": agent_id,
                                "thought": thought_data.get("missing", ""),
                                "enough": thought_data.get("enough", False),
                            })}

                        if node_state.get("search_query"):
                            yield {"event": "act", "data": json.dumps({
                                "agent_id": agent_id,
                                "action": "search",
                                "query": node_state.get("search_query"),
                            })}

                        loaded = node_state.get("loaded_knowledge", [])
                        if loaded:
                            yield {"event": "observe", "data": json.dumps({
                                "agent_id": agent_id,
                                "found_nodes": len(loaded),
                                "enough": node_state.get("enough", False),
                            })}

                answer = ""
                sources = []
                if final_state:
                    last = list(final_state.values())[-1] if final_state else {}
                    answer = last.get("final_answer", "")
                    sources = last.get("sources", [])

                if answer:
                    yield {"event": "answer_chunk", "data": json.dumps({"text": answer})}

                for i, s in enumerate(sources or [], 1):
                    yield {"event": "source_linked", "data": json.dumps({
                        "marker": f"N{i}", "node_id": s.get("node_id"), "title": s.get("title"),
                    })}

                yield {"event": "answer_complete", "data": json.dumps({
                    "full_text": answer,
                    "sources": [{"N": i, "title": s.get("title"), "node_id": s.get("node_id")}
                                for i, s in enumerate(sources or [], 1)],
                })}

        except Exception as e:
            import traceback
            traceback.print_exc()
            yield {"event": "error", "data": json.dumps({"message": str(e)})}

    return EventSourceResponse(event_stream())
