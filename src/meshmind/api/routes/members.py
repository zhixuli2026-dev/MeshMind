from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from meshmind.db.engine import AsyncSessionFactory
from meshmind.db.repositories.authors import AuthorRepository

router = APIRouter(prefix="/workspaces/{workspace_id}/members", tags=["members"])


class AddMemberRequest(BaseModel):
    user_id: str
    name: str | None = None


@router.get("")
async def list_members(workspace_id: str):
    async with AsyncSessionFactory() as session:
        from sqlalchemy import select
        from meshmind.db.models import AuthorModel
        result = await session.execute(
            select(AuthorModel).where(AuthorModel.workspace_id == UUID(workspace_id))
        )
        authors = result.scalars().all()
        return {
            "members": [
                {"author_id": str(a.author_id), "user_id": a.user_id, "name": a.name}
                for a in authors
            ]
        }


@router.post("")
async def add_member(workspace_id: str, body: AddMemberRequest):
    async with AsyncSessionFactory() as session:
        repo = AuthorRepository(session)
        author = await repo.get_or_create(UUID(workspace_id), body.user_id, body.name)
        await session.commit()
        return {"author_id": str(author.author_id), "user_id": author.user_id, "name": author.name}


@router.delete("/{user_id}")
async def remove_member(workspace_id: str, user_id: str):
    async with AsyncSessionFactory() as session:
        from sqlalchemy import select, delete
        from meshmind.db.models import AuthorModel
        result = await session.execute(
            select(AuthorModel).where(
                AuthorModel.workspace_id == UUID(workspace_id),
                AuthorModel.user_id == user_id,
            )
        )
        author = result.scalar_one_or_none()
        if author is None:
            raise HTTPException(status_code=404, detail="Member not found")
        await session.delete(author)
        await session.commit()
        return {"deleted": True}
