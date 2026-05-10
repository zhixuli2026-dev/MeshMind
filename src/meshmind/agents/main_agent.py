from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from meshmind.agents.knowledge_agent import create_knowledge_agent
from meshmind.core.graph import KnowledgeGraph
from meshmind.core.maintenance import MaintenanceService
from meshmind.core.retrieval import KnowledgeRetrieval
from meshmind.embedding.encoder import EmbeddingEncoder
from meshmind.llm.harness import LLMHarness


class MainAgent:
    def __init__(
        self,
        harness: LLMHarness,
        encoder: EmbeddingEncoder,
        session: AsyncSession,
        workspace_id: UUID,
    ):
        self.harness = harness
        self.encoder = encoder
        self.session = session
        self.workspace_id = workspace_id
        self.retrieval = KnowledgeRetrieval(session, workspace_id)
        self.graph = KnowledgeGraph(session, workspace_id)
        self.maintenance = MaintenanceService(harness)

    async def ask(self, question: str) -> dict:
        agent = create_knowledge_agent(
            harness=self.harness,
            retrieval=self.retrieval,
            encoder=self.encoder,
        )

        initial_state = {
            "question": question,
            "workspace_id": str(self.workspace_id),
            "loaded_knowledge": [],
            "missing": [],
            "enough": False,
        }

        final_state = None
        async for event in agent.astream(initial_state):
            final_state = event

        if final_state is None:
            return {"answer": "Failed to process question", "sources": []}

        state_values = list(final_state.values())[-1] if final_state else {}
        answer = state_values.get("final_answer", "")
        sources = state_values.get("sources", [])

        # Process positive feedback for used knowledge
        used_node_ids = [UUID(s["node_id"]) for s in sources if s.get("node_id")]
        if used_node_ids and answer:
            await self.maintenance.process_feedback(
                self.graph, question, answer, used_node_ids,
            )

        return {"answer": answer, "sources": sources}
