import uuid
from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from poly_db.models.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    def __init__(self, model: type[T], session: Session):
        self.model = model
        self.session = session

    def get(self, id: uuid.UUID) -> T | None:
        return self.session.get(self.model, id)

    def get_by_id(self, id: uuid.UUID) -> T | None:
        return self.get(id)

    def list(self) -> list[T]:
        stmt = select(self.model)
        return list(self.session.scalars(stmt).all())

    def create(self, obj: T | None = None, **kwargs: Any) -> T:
        if obj is None:
            obj = self.model(**kwargs)
        elif kwargs:
            raise ValueError("Provide either an object or keyword arguments, not both.")
        self.session.add(obj)
        self.session.flush()
        return obj

    def update(self, id_or_obj: uuid.UUID | T, **kwargs: Any) -> T | None:
        obj = id_or_obj if isinstance(id_or_obj, self.model) else self.get(id_or_obj)
        if obj:
            for key, value in kwargs.items():
                setattr(obj, key, value)
            self.session.flush()
        return obj

    def delete(self, id: uuid.UUID) -> bool:
        obj = self.get(id)
        if obj:
            self.session.delete(obj)
            self.session.flush()
            return True
        return False
