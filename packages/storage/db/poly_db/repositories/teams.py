import uuid
from datetime import UTC, datetime

from sqlalchemy import select

from poly_db.models.team_invitations import TeamInvitation
from poly_db.models.team_members import TeamMember
from poly_db.models.teams import Team
from poly_db.repositories.base import BaseRepository


class TeamRepository(BaseRepository[Team]):
    def __init__(self, session):
        super().__init__(Team, session)

    def get_by_name(self, name: str) -> Team | None:
        stmt = select(Team).where(Team.name == name)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_stripe_customer_id(self, customer_id: str) -> Team | None:
        stmt = select(Team).where(Team.stripe_customer_id == customer_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_stripe_subscription_id(self, subscription_id: str) -> Team | None:
        stmt = select(Team).where(Team.stripe_subscription_id == subscription_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def list_by_plan(self, plan: str) -> list[Team]:
        stmt = select(Team).where(Team.plan == plan)
        return self.session.execute(stmt).scalars().all()

    def list_suspended(self) -> list[Team]:
        stmt = select(Team).where(Team.is_suspended.is_(True))
        return self.session.execute(stmt).scalars().all()


class TeamMemberRepository(BaseRepository[TeamMember]):
    def __init__(self, session):
        super().__init__(TeamMember, session)

    def get_by_team_id(self, team_id: uuid.UUID) -> list[TeamMember]:
        stmt = select(TeamMember).where(TeamMember.team_id == team_id)
        return self.session.execute(stmt).scalars().all()

    def list_by_user_id(self, user_id: uuid.UUID) -> list[TeamMember]:
        stmt = select(TeamMember).where(TeamMember.user_id == user_id)
        return self.session.execute(stmt).scalars().all()

    def get_by_user_and_team(self, user_id: uuid.UUID, team_id: uuid.UUID) -> TeamMember | None:
        stmt = select(TeamMember).where(
            TeamMember.user_id == user_id,
            TeamMember.team_id == team_id,
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def count_admins(self, team_id: uuid.UUID) -> int:
        stmt = select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.role == "ADMIN",
        )
        return len(self.session.execute(stmt).scalars().all())


class TeamInvitationRepository(BaseRepository[TeamInvitation]):
    def __init__(self, session):
        super().__init__(TeamInvitation, session)

    def list_by_team_id(self, team_id: uuid.UUID) -> list[TeamInvitation]:
        stmt = (
            select(TeamInvitation)
            .where(TeamInvitation.team_id == team_id)
            .order_by(TeamInvitation.created_at.desc())
        )
        return self.session.execute(stmt).scalars().all()

    def get_by_token(self, token: str) -> TeamInvitation | None:
        stmt = select(TeamInvitation).where(TeamInvitation.token == token)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_email(self, team_id: uuid.UUID, email: str) -> list[TeamInvitation]:
        stmt = select(TeamInvitation).where(
            TeamInvitation.team_id == team_id,
            TeamInvitation.email == email,
        )
        return self.session.execute(stmt).scalars().all()

    def delete_expired(self) -> list[TeamInvitation]:
        now = datetime.now(UTC)
        stmt = select(TeamInvitation).where(TeamInvitation.expires_at < now)
        expired = self.session.execute(stmt).scalars().all()
        for invitation in expired:
            self.session.delete(invitation)
        self.session.flush()
        return expired
