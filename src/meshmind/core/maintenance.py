import json
from uuid import UUID

from pydantic import BaseModel

from meshmind.core.graph import KnowledgeGraph
from meshmind.llm.harness import LLMHarness, TaskType
from meshmind.llm.prompts import MAINTENANCE_CHECK


class MaintenanceResult(BaseModel):
    helpful: bool
    reasoning: str = ""


class MaintenanceService:
    def __init__(self, harness: LLMHarness):
        self.harness = harness

    async def evaluate_feedback(
        self,
        question: str,
        answer: str,
        node_title: str,
        node_summary: str,
    ) -> MaintenanceResult:
        prompt = MAINTENANCE_CHECK.format(
            question=question,
            answer=answer,
            node_title=node_title,
            node_summary=node_summary,
        )
        return await self.harness.call_structured(
            messages=[{"role": "user", "content": prompt}],
            task=TaskType.MAINTENANCE_JUDGMENT,
            output_model=MaintenanceResult,
        )

    async def process_feedback(
        self,
        graph: KnowledgeGraph,
        question: str,
        answer: str,
        used_nodes: list[UUID],
    ) -> None:
        for node_id in used_nodes:
            node = await graph.nodes.get_by_id(node_id)
            if node is None:
                continue
            result = await self.evaluate_feedback(
                question=question,
                answer=answer,
                node_title=node.title,
                node_summary=node.summary,
            )
            if result.helpful:
                from meshmind.core.lifecycle import compute_new_half_life
                new_hl = compute_new_half_life(node.half_life, node.knowledge_type)
                await graph.vitality.record_event(
                    node_id=node_id,
                    vitality=node.vitality,
                    half_life=new_hl,
                    event_type="positive_feedback",
                    context={"question": question[:200]},
                )
                await graph.nodes.update(node, half_life=new_hl)
