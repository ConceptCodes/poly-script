from sqlalchemy.orm import Session
from sqlalchemy import select
from ..models.users import User
from .base import BaseRepository
from typing import Optional


class UserRepository(BaseRepository[User]):
    def __init__(self, session: Session):
        super().__init__(User, session)

    def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        return self.session.scalar(stmt)

    def get_by_verification_token(self, token: str) -> Optional[User]:
        stmt = select(User).where(User.verification_token == token)
        return self.session.scalar(stmt)
