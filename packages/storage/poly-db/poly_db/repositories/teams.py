from .base import BaseRepository
from ..models.team_members import TeamMember
from ..models.team_invitations import TeamInvitation
from sqlalchemy import select
import uuid
from typing import Optional, List


class TeamMemberRepository(BaseRepository[TeamMember]):
    def __init__(self, session):
        super().__init__(TeamMember, session)

    def get_by_team_id(self, team_id: uuid.UUID) -> List[TeamMember]:
        stmt = select(TeamMember).where(TeamMember.team_id == team_id)
        return self.session.execute(stmt).scalars().all()

    def get_by_user_id(self, user_id: uuid.UUID) -> List[TeamMember]:
        stmt = select(TeamMember).where(TeamMember.user_id == user_id)
        return self.session.execute(stmt).scalars().all()


class TeamInvitationRepository(BaseRepository[TeamInvitation]):
    def __init__(self, session):
        super().__init__(TeamInvitation, session)

    def get_by_token(self, token: str) -> Optional[TeamInvitation]:
        stmt = select(TeamInvitation).where(TeamInvitation.token == token)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_email(self, email: str) -> List[TeamInvitation]:
        stmt = select(TeamInvitation).where(TeamInvitation.email == email)
        return self.session.execute(stmt).scalars().all()
