from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from ..models.base import Base
import uuid

T = TypeVar("T", bound=Base)

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], session: Session):
        self.model = model
        self.session = session

    def get(self, id: uuid.UUID) -> Optional[T]:
        return self.session.get(self.model, id)

    def list(self) -> List[T]:
        stmt = select(self.model)
        return list(self.session.scalars(stmt).all())

    def create(self, **kwargs: Any) -> T:
        obj = self.model(**kwargs)
        self.session.add(obj)
        self.session.flush()
        return obj

    def update(self, id: uuid.UUID, **kwargs: Any) -> Optional[T]:
        obj = self.get(id)
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
