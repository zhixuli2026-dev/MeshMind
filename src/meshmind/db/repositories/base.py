from typing import TypeVar
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from meshmind.db.engine import Base

T = TypeVar("T", bound=Base)


class BaseRepository:
    model: type[Base]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: UUID) -> Base | None:
        result = await self.session.execute(
            select(self.model).where(self.model.__table__.c.values()[0] == id)
        )
        return result.scalar_one_or_none()

    async def list_all(self, *, limit: int = 100, offset: int = 0) -> list[Base]:
        result = await self.session.execute(
            select(self.model).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def create(self, **kwargs) -> Base:
        entity = self.model(**kwargs)
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def update(self, entity: Base, **kwargs) -> Base:
        for key, value in kwargs.items():
            setattr(entity, key, value)
        await self.session.flush()
        return entity

    async def delete(self, entity: Base) -> None:
        await self.session.delete(entity)
        await self.session.flush()
