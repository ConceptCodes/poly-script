from sqlalchemy import select
from sqlalchemy.orm import Session

from poly_db.models.users import User
from poly_db.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: Session):
        super().__init__(User, session)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self.session.scalar(stmt)

    def get_by_verification_token(self, token: str) -> User | None:
        stmt = select(User).where(User.verification_token == token)
        return self.session.scalar(stmt)
