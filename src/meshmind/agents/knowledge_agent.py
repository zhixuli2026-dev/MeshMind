import json
import uuid
from typing import Literal

from langgraph.graph import END, StateGraph
from langgraph.types import StreamWriter

from meshmind.agents.state import AgentState
from meshmind.core.retrieval import KnowledgeRetrieval
from meshmind.embedding.encoder import EmbeddingEncoder
from meshmind.llm.harness import LLMHarness, TaskType
from meshmind.llm.prompts import AGENT_THINK, COMPOSE_ANSWER


def create_knowledge_agent(
    harness: LLMHarness,
    retrieval: KnowledgeRetrieval,
    encoder: EmbeddingEncoder,
    agent_id: str | None = None,
) -> StateGraph:
    agent_id = agent_id or str(uuid.uuid4())[:8]

    async def think(state: AgentState, writer: StreamWriter) -> AgentState:
        loaded = "\n".join(
            f"- [{k['title']}]: {k['summary']}" for k in state.get("loaded_knowledge", [])
        ) or "(no knowledge loaded yet)"

        prompt = AGENT_THINK.format(
            question=state["question"],
            loaded_knowledge=loaded,
        )
        resp = await harness.call(
            messages=[{"role": "user", "content": prompt}],
            task=TaskType.AGENT_THINK,
            max_tokens=1024,
            use_json=True,
        )
        try:
            data = json.loads(resp.content)
        except json.JSONDecodeError:
            data = {"enough": False, "missing": [], "search_query": state["question"]}

        writer(("think", {"agent_id": agent_id, "thought": data.get("missing", ""), "enough": data.get("enough", False)}))

        return {
            **state,
            "enough": data.get("enough", False),
            "missing": data.get("missing", []),
            "search_query": data.get("search_query"),
            "current_thought": json.dumps(data),
        }

    async def act(state: AgentState, writer: StreamWriter) -> AgentState:
        query = state.get("search_query") or state["question"]
        embedding = encoder.encode_single(query)

        writer(("act", {"agent_id": agent_id, "action": "search", "query": query}))

        results = await retrieval.hybrid_search(query, embedding=embedding)
        current = state.get("loaded_knowledge", [])
        new_nodes = [r for r in results if r["node_id"] not in {k["node_id"] for k in current}]

        return {
            **state,
            "loaded_knowledge": current + new_nodes,
        }

    async def observe(state: AgentState, writer: StreamWriter) -> AgentState:
        loaded_count = len(state.get("loaded_knowledge", []))
        writer(("observe", {
            "agent_id": agent_id,
            "found_nodes": loaded_count,
            "enough": state.get("enough", False),
        }))
        return state

    def should_continue(state: AgentState) -> Literal["think", "end"]:
        if state.get("enough", False):
            return "end"
        if len(state.get("loaded_knowledge", [])) >= 50:
            return "end"
        for _ in range(1):  # single check
            if len(state.get("loaded_knowledge", [])) >= 3:
                return "end"
        return "think"

    async def compose(state: AgentState, writer: StreamWriter) -> AgentState:
        knowledge_context = ""
        sources = []
        for i, k in enumerate(state.get("loaded_knowledge", [])[:20], 1):
            knowledge_context += f"[{i}] {k['title']}: {k['summary']}\n"
            sources.append({"N": i, "title": k["title"], "node_id": k["node_id"]})

        prompt = COMPOSE_ANSWER.format(
            question=state["question"],
            knowledge_context=knowledge_context,
        )
        resp = await harness.call(
            messages=[{"role": "user", "content": prompt}],
            task=TaskType.FINAL_ANSWER,
            max_tokens=2048,
        )

        writer(("answer_complete", {
            "agent_id": agent_id,
            "full_text": resp.content,
            "sources": sources,
        }))

        return {**state, "final_answer": resp.content, "sources": sources}

    graph = StateGraph(AgentState)
    graph.add_node("think", think)
    graph.add_node("act", act)
    graph.add_node("observe", observe)
    graph.add_node("compose", compose)

    graph.set_entry_point("think")
    graph.add_edge("think", "act")
    graph.add_edge("act", "observe")
    graph.add_conditional_edges("observe", should_continue, {"think": "think", "end": "compose"})
    graph.add_edge("compose", END)

    return graph.compile()
