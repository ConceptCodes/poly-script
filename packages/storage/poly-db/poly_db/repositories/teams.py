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

    def list_by_user_id(self, user_id: uuid.UUID) -> List[TeamMember]:
        stmt = select(TeamMember).where(TeamMember.user_id == user_id)
        return self.session.execute(stmt).scalars().all()

    def get_by_user_and_team(self, user_id: uuid.UUID, team_id: uuid.UUID) -> Optional[TeamMember]:
        stmt = select(TeamMember).where(
            TeamMember.user_id == user_id,
            TeamMember.team_id == team_id,
        )
        return self.session.execute(stmt).scalar_one_or_none()


class TeamInvitationRepository(BaseRepository[TeamInvitation]):
    def __init__(self, session):
        super().__init__(TeamInvitation, session)

    def list_by_team_id(self, team_id: uuid.UUID) -> List[TeamInvitation]:
        stmt = (
            select(TeamInvitation)
            .where(TeamInvitation.team_id == team_id)
            .order_by(TeamInvitation.created_at.desc())
        )
        return self.session.execute(stmt).scalars().all()

    def get_by_token(self, token: str) -> Optional[TeamInvitation]:
        stmt = select(TeamInvitation).where(TeamInvitation.token == token)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_email(self, team_id: uuid.UUID, email: str) -> List[TeamInvitation]:
        stmt = select(TeamInvitation).where(
            TeamInvitation.team_id == team_id,
            TeamInvitation.email == email,
        )
        return self.session.execute(stmt).scalars().all()

    def delete_expired(self) -> List[TeamInvitation]:
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        stmt = select(TeamInvitation).where(TeamInvitation.expires_at < now)
        expired = self.session.execute(stmt).scalars().all()
        for invitation in expired:
            self.session.delete(invitation)
        self.session.flush()
        return expired
