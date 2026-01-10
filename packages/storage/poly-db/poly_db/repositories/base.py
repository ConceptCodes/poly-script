from typing import Generic, TypeVar, Type, Optional, List, Any, Union
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

    def get_by_id(self, id: uuid.UUID) -> Optional[T]:
        return self.get(id)

    def list(self) -> List[T]:
        stmt = select(self.model)
        return list(self.session.scalars(stmt).all())

    def create(self, obj: Optional[T] = None, **kwargs: Any) -> T:
        if obj is None:
            obj = self.model(**kwargs)
        elif kwargs:
            raise ValueError("Provide either an object or keyword arguments, not both.")
        self.session.add(obj)
        self.session.flush()
        return obj

    def update(self, id_or_obj: Union[uuid.UUID, T], **kwargs: Any) -> Optional[T]:
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
