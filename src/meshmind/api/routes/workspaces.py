import uuid
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from meshmind.db.engine import AsyncSessionFactory
from meshmind.db.models import WorkspaceModel

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


class CreateWorkspaceRequest(BaseModel):
    name: str
    description: str = ""


class WorkspaceResponse(BaseModel):
    workspace_id: str
    name: str
    description: str | None
    api_key: str
    created_at: str | None


@router.post("", response_model=WorkspaceResponse)
async def create_workspace(body: CreateWorkspaceRequest):
    from passlib.hash import bcrypt

    api_key = f"msm_{uuid.uuid4().hex}"
    key_hash = bcrypt.hash(api_key)

    async with AsyncSessionFactory() as session:
        ws = WorkspaceModel(
            name=body.name,
            description=body.description,
            api_key_hash=key_hash,
        )
        session.add(ws)
        await session.commit()
        await session.refresh(ws)

        return WorkspaceResponse(
            workspace_id=str(ws.workspace_id),
            name=ws.name,
            description=ws.description,
            api_key=api_key,
            created_at=ws.created_at.isoformat() if ws.created_at else None,
        )


@router.get("/{workspace_id}")
async def get_workspace(workspace_id: str):
    async with AsyncSessionFactory() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(WorkspaceModel).where(WorkspaceModel.workspace_id == UUID(workspace_id))
        )
        ws = result.scalar_one_or_none()
        if ws is None:
            raise HTTPException(status_code=404, detail="Workspace not found")
        return {
            "workspace_id": str(ws.workspace_id),
            "name": ws.name,
            "description": ws.description,
            "created_at": ws.created_at.isoformat() if ws.created_at else None,
        }


@router.get("/{workspace_id}/stats")
async def get_workspace_stats(workspace_id: str):
    async with AsyncSessionFactory() as session:
        from sqlalchemy import text
        result = await session.execute(text("""
            SELECT knowledge_type, COUNT(*) as cnt
            FROM meshmind.knowledge_nodes
            WHERE workspace_id = :ws_id AND is_active = TRUE
            GROUP BY knowledge_type
        """), {"ws_id": UUID(workspace_id)})
        type_dist = {row[0]: row[1] for row in result.fetchall()}

        total = await session.execute(text(
            "SELECT COUNT(*) FROM meshmind.knowledge_nodes WHERE workspace_id = :ws_id AND is_active = TRUE"
        ), {"ws_id": UUID(workspace_id)})
        node_count = total.scalar()

        return {"node_count": node_count, "type_distribution": type_dist}
