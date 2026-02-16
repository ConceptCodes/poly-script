"""Async version of Team repositories for use with SQLAlchemy AsyncSession."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from poly_db.models.team_invitations import TeamInvitation
from poly_db.models.team_members import TeamMember
from poly_db.models.teams import Team
from poly_db.repositories.base_async import BaseRepositoryAsync


class TeamRepositoryAsync(BaseRepositoryAsync[Team]):
    """Async repository for Team operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Team, session)

    async def get_by_name(self, name: str) -> Team | None:
        """Get a team by its name."""
        stmt = select(Team).where(Team.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_stripe_customer_id(self, customer_id: str) -> Team | None:
        """Get a team by its Stripe customer ID."""
        stmt = select(Team).where(Team.stripe_customer_id == customer_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_stripe_subscription_id(self, subscription_id: str) -> Team | None:
        """Get a team by its Stripe subscription ID."""
        stmt = select(Team).where(Team.stripe_subscription_id == subscription_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_plan(self, plan: str) -> list[Team]:
        """List all teams with a specific plan."""
        stmt = select(Team).where(Team.plan == plan)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_suspended(self) -> list[Team]:
        """List all suspended teams."""
        stmt = select(Team).where(Team.is_suspended.is_(True))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class TeamMemberRepositoryAsync(BaseRepositoryAsync[TeamMember]):
    """Async repository for TeamMember operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(TeamMember, session)

    async def get_by_team_id(self, team_id: uuid.UUID) -> list[TeamMember]:
        """Get all team members for a specific team."""
        stmt = select(TeamMember).where(TeamMember.team_id == team_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_user_id(self, user_id: uuid.UUID) -> list[TeamMember]:
        """Get all team memberships for a specific user."""
        stmt = select(TeamMember).where(TeamMember.user_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_user_and_team(
        self, user_id: uuid.UUID, team_id: uuid.UUID
    ) -> TeamMember | None:
        """Get a team membership by user and team."""
        stmt = select(TeamMember).where(
            TeamMember.user_id == user_id,
            TeamMember.team_id == team_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_admins(self, team_id: uuid.UUID) -> int:
        """Count the number of admins in a team."""
        stmt = select(func.count(TeamMember.id)).where(
            TeamMember.team_id == team_id,
            TeamMember.role == "ADMIN",
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0


class TeamInvitationRepositoryAsync(BaseRepositoryAsync[TeamInvitation]):
    """Async repository for TeamInvitation operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(TeamInvitation, session)

    async def list_by_team_id(self, team_id: uuid.UUID) -> list[TeamInvitation]:
        """List all invitations for a specific team."""
        stmt = (
            select(TeamInvitation)
            .where(TeamInvitation.team_id == team_id)
            .order_by(TeamInvitation.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_token(self, token: str) -> TeamInvitation | None:
        """Get an invitation by its token."""
        stmt = select(TeamInvitation).where(TeamInvitation.token == token)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, team_id: uuid.UUID, email: str) -> list[TeamInvitation]:
        """Get all invitations for a specific email in a team."""
        stmt = select(TeamInvitation).where(
            TeamInvitation.team_id == team_id,
            TeamInvitation.email == email,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_expired(self) -> list[TeamInvitation]:
        """Delete all expired invitations and return them."""
        now = datetime.now(UTC)
        stmt = select(TeamInvitation).where(TeamInvitation.expires_at < now)
        result = await self.session.execute(stmt)
        expired = list(result.scalars().all())

        for invitation in expired:
            await self.session.delete(invitation)

        await self.session.flush()
        return expired
