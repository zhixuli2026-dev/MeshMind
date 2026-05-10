from typing import TypedDict


class AgentState(TypedDict, total=False):
    """State shared across the LangGraph agent nodes."""

    question: str
    workspace_id: str
    loaded_knowledge: list[dict]        # knowledge nodes loaded so far
    missing: list[str]                  # topics still needed
    current_thought: str                # latest Think output
    enough: bool                        # is knowledge sufficient?
    search_query: str | None            # next search query
    final_answer: str                   # composed answer
    sources: list[dict]                 # source citations [{"N": 1, "title": "...", "node_id": "..."}]
    error: str | None                   # error message if any
