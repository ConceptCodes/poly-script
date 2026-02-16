"""Async version of BaseRepository for use with SQLAlchemy AsyncSession."""

from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from poly_db.models.base import Base

T = TypeVar("T", bound=Base)


class BaseRepositoryAsync(Generic[T]):
    """Async repository base class with CRUD operations using AsyncSession."""

    def __init__(self, model: type[T], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, id: Any) -> T | None:
        """Get entity by ID using async session.get()."""
        return await self.session.get(self.model, id)

    async def get_by_id(self, id: Any) -> T | None:
        """Alias for get() to maintain interface compatibility."""
        return await self.get(id)

    async def list(self) -> list[T]:
        """List all entities."""
        stmt = select(self.model)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, obj: T | None = None, **kwargs: Any) -> T:
        """Create a new entity."""
        if obj is None:
            obj = self.model(**kwargs)
        elif kwargs:
            raise ValueError("Provide either an object or keyword arguments, not both.")
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def update(self, id_or_obj: Any | T, **kwargs: Any) -> T | None:
        """Update an entity by ID or object."""
        obj = id_or_obj if isinstance(id_or_obj, self.model) else await self.get(id_or_obj)
        if obj:
            for key, value in kwargs.items():
                setattr(obj, key, value)
            await self.session.flush()
        return obj

    async def delete(self, id: Any) -> bool:
        """Delete entity by ID."""
        obj = await self.get(id)
        if obj:
            await self.session.delete(obj)
            await self.session.flush()
            return True
        return False
