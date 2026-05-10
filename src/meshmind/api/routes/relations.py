from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from meshmind.db.engine import AsyncSessionFactory
from meshmind.db.repositories.relations import RelationRepository

router = APIRouter(prefix="/workspaces/{workspace_id}/relations", tags=["relations"])


class CreateRelationRequest(BaseModel):
    source_node_id: str
    target_node_id: str
    relation_type: str


@router.post("")
async def create_relation(workspace_id: str, body: CreateRelationRequest):
    async with AsyncSessionFactory() as session:
        repo = RelationRepository(session)
        existing = await repo.find_between(UUID(body.source_node_id), UUID(body.target_node_id))
        if existing and existing.relation_type == body.relation_type:
            return {"relationship_id": str(existing.relationship_id), "status": "already_exists"}

        rel = await repo.create(
            workspace_id=UUID(workspace_id),
            source_node_id=UUID(body.source_node_id),
            target_node_id=UUID(body.target_node_id),
            relation_type=body.relation_type,
        )
        await session.commit()
        return {"relationship_id": str(rel.relationship_id), "status": "created"}


@router.delete("/{relation_id}")
async def delete_relation(workspace_id: str, relation_id: str):
    async with AsyncSessionFactory() as session:
        repo = RelationRepository(session)
        rel = await repo.get_by_id(UUID(relation_id))
        if rel is None:
            raise HTTPException(status_code=404, detail="Relation not found")
        await repo.delete(rel)
        await session.commit()
        return {"deleted": True}
