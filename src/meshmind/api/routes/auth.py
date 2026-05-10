from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from jose import jwt

from meshmind.core.config import settings
from meshmind.db.engine import AsyncSessionFactory
from meshmind.db.models import WorkspaceModel

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    workspace_id: str
    user_id: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    workspace_id: str


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    async with AsyncSessionFactory() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(WorkspaceModel).where(WorkspaceModel.workspace_id == UUID(body.workspace_id))
        )
        ws = result.scalar_one_or_none()
        if ws is None:
            raise HTTPException(status_code=404, detail="Workspace not found")

        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
        payload = {
            "sub": body.user_id,
            "workspace_id": body.workspace_id,
            "exp": expire,
        }
        token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

        return TokenResponse(
            access_token=token,
            workspace_id=body.workspace_id,
        )
