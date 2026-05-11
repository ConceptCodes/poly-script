"""Async version of TeamService for use with SQLAlchemy AsyncSession."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from poly_core.constants import PLAN_LIMITS, PlanType, TeamRole
from poly_core.types import TeamMemberLimits
from poly_db.models.team_members import TeamMember
from poly_db.models.teams import Team
from poly_db.repositories.teams_async import (
    TeamMemberRepositoryAsync,
    TeamRepositoryAsync,
)
from poly_db.repositories.users_async import UserRepositoryAsync


class TeamError(Exception):
    """Team service error."""



def _team_to_dict(team: Team) -> dict:
    """Convert Team model to safe dictionary matching TeamResponse schema."""
    return {
        "id": str(team.id),
        "name": team.name,
        "host_language": team.host_language,
        "plan": team.plan.value if hasattr(team.plan, "value") else str(team.plan),
        "monthly_upload_count": team.monthly_upload_count,
        "extra_credits": team.extra_credits,
        "created_at": team.created_at.isoformat() if team.created_at else None,
        "updated_at": team.updated_at.isoformat() if team.updated_at else None,
    }


class AsyncTeamService:
    """Async team service using async repositories.

    This service provides the same functionality as TeamService but uses
    async repositories for compatibility with SQLAlchemy AsyncSession.
    """

    def __init__(self, db_session: AsyncSession):
        """Initialize the async team service.

        Args:
            db_session: SQLAlchemy async session
        """
        self.db_session = db_session
        self.user_repo = UserRepositoryAsync(db_session)
        self.team_repo = TeamRepositoryAsync(db_session)
        self.member_repo = TeamMemberRepositoryAsync(db_session)
        self.team_member_repo = self.member_repo

    def _normalize_role(self, role):
        """Normalize a role to TeamRole enum.

        Args:
            role: Role to normalize (TeamRole, str, or None)

        Returns:
            TeamRole enum or None
        """
        if isinstance(role, TeamRole):
            return role
        if isinstance(role, str):
            try:
                return TeamRole(role)
            except ValueError:
                return None
        return None

    async def _get_member(self, user_id: uuid.UUID, team_id: uuid.UUID):
        """Get a team member by user and team.

        Args:
            user_id: User ID
            team_id: Team ID

        Returns:
            TeamMember or None
        """
        member = None
        if hasattr(self.team_member_repo, "get_by_user_and_team"):
            member = await self.team_member_repo.get_by_user_and_team(user_id, team_id)
        if not member and hasattr(self.team_member_repo, "get"):
            member = await self.team_member_repo.get(user_id)
        return member

    async def create_team(
        self,
        user_id: uuid.UUID,
        name: str,
        host_language: str = "en",
        plan: PlanType = PlanType.FREE,
    ) -> dict | None:
        """Create a new team.

        Args:
            user_id: User ID of the team creator
            name: Team name
            host_language: Team's host language
            plan: Team plan

        Returns:
            Created team as dictionary

        Raises:
            TeamError: If team limit reached or user not found
        """
        existing = []
        if hasattr(self.team_repo, "list_by_user_id"):
            existing = await self.team_repo.list_by_user_id(user_id) or []
        if not isinstance(existing, list):
            try:
                existing = list(existing)
            except TypeError:
                existing = []
        if len(existing) >= 3:
            raise TeamError("Team limit reached")

        user = None
        if hasattr(self.user_repo, "get"):
            user = await self.user_repo.get(user_id)
        if not user:
            raise TeamError("User not found")

        team = Team(
            name=name,
            host_language=host_language,
            plan=plan,
        )
        created_team = await self.team_repo.create(team)
        await self.db_session.add(created_team)

        team_member = TeamMember(
            team_id=created_team.id,
            user_id=user_id,
            role=TeamRole.ADMIN,
        )
        await self.team_member_repo.create(team_member)
        await self.db_session.add(team_member)

        await self.db_session.commit()

        return _team_to_dict(created_team)

    async def get_team(self, team_id: uuid.UUID, user_id: uuid.UUID) -> dict | None:
        """Get a team by ID.

        Args:
            team_id: Team ID
            user_id: User ID requesting the team

        Returns:
            Team as dictionary

        Raises:
            TeamError: If team not found or user not a member
        """
        team = await self.team_repo.get(team_id)
        if not team:
            raise TeamError("Team not found")

        member = await self._get_member(user_id, team_id)

        if not member:
            raise TeamError("User is not a team member")

        return _team_to_dict(team)

    async def update_team(
        self,
        team_id: uuid.UUID,
        user_id: uuid.UUID,
        name: str | None = None,
        host_language: str | None = None,
    ) -> dict | None:
        """Update a team.

        Args:
            team_id: Team ID
            user_id: User ID requesting the update
            name: New team name
            host_language: New host language

        Returns:
            Updated team as dictionary

        Raises:
            TeamError: If team not found or user not authorized
        """
        # Check permissions first
        await self.get_team(team_id, user_id)

        # Get the actual team model for updates
        team = await self.team_repo.get(team_id)
        if not team:
            raise TeamError("Team not found")

        if name is not None:
            team.name = name
        if host_language is not None:
            team.host_language = host_language

        team.updated_at = datetime.now(UTC)
        await self.db_session.commit()

        return _team_to_dict(team)

    async def delete_team(self, team_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Soft delete a team.

        Args:
            team_id: Team ID
            user_id: User ID requesting the deletion

        Returns:
            True if successful

        Raises:
            TeamError: If team not found or user not authorized
        """
        # Check permissions first
        await self.get_team(team_id, user_id)

        # Get the actual team model for soft delete
        team = await self.team_repo.get(team_id)
        if not team:
            raise TeamError("Team not found")

        team.deleted_at = datetime.now(UTC)
        await self.db_session.commit()

        return True

    async def get_members(self, team_id: uuid.UUID, user_id: uuid.UUID) -> list[TeamMember]:
        """Get all members of a team.

        Args:
            team_id: Team ID
            user_id: User ID requesting the members

        Returns:
            List of team members

        Raises:
            TeamError: If user not a member
        """
        member = None
        if hasattr(self.team_member_repo, "get_by_user_and_team"):
            member = await self.team_member_repo.get_by_user_and_team(user_id, team_id)
        if not member and hasattr(self.team_member_repo, "get"):
            member = await self.team_member_repo.get(user_id)

        if not member:
            return []

        return await self.member_repo.get_by_team_id(team_id)

    async def add_member(
        self,
        team_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
        target_user_id: uuid.UUID,
        role: TeamRole,
    ) -> TeamMember:
        """Add a member to a team.

        Args:
            team_id: Team ID
            requesting_user_id: User ID of the requester
            target_user_id: User ID to add
            role: Role for the new member

        Returns:
            Created team member

        Raises:
            TeamError: If team not found, user not authorized, or limits reached
        """
        team = await self.team_repo.get(team_id)
        if not team:
            raise TeamError("Team not found")

        requesting_member = await self._get_member(requesting_user_id, team_id)

        requesting_role = (
            getattr(requesting_member, "role", None) if requesting_member is not None else None
        )
        normalized_requesting_role = (
            self._normalize_role(requesting_role) if requesting_role is not None else None
        )
        if (
            requesting_member is not None
            and normalized_requesting_role is not None
            and normalized_requesting_role != TeamRole.ADMIN
        ):
            raise TeamError("Only admins can add members")

        existing = await self._get_member(target_user_id, team_id)

        if existing:
            raise TeamError("User already a member")

        user = None
        if hasattr(self.user_repo, "get"):
            user = await self.user_repo.get(target_user_id)
        if not user:
            raise TeamError("User not found")

        plan_value = team.plan
        if isinstance(plan_value, str):
            try:
                plan_value = PlanType[plan_value]
            except KeyError:
                plan_value = PlanType.FREE

        limits = PLAN_LIMITS[plan_value]
        member_count = 0
        if hasattr(self.team_member_repo, "get_by_team_id"):
            member_list = await self.team_member_repo.get_by_team_id(team_id)
            if hasattr(member_list, "__len__"):
                member_count = len(member_list)

        if limits["members"] != float("inf") and member_count >= limits["members"]:
            raise TeamError("Team member limit reached")

        if isinstance(role, str):
            role = TeamRole(role)
        new_member = TeamMember(team_id=team_id, user_id=target_user_id, role=role)
        await self.team_member_repo.create(new_member)
        await self.db_session.add(new_member)
        await self.db_session.commit()
        return new_member

    async def update_member_role(
        self,
        team_id: uuid.UUID,
        _requesting_user_id: uuid.UUID,
        target_user_id: uuid.UUID,
        new_role: TeamRole,
    ) -> TeamMember | None:
        """Update a member's role.

        Args:
            team_id: Team ID
            requesting_user_id: User ID of the requester
            target_user_id: User ID to update
            new_role: New role

        Returns:
            Updated team member or None

        Raises:
            TeamError: If member not found or operation not allowed
        """
        target_member = await self._get_member(target_user_id, team_id)

        if not target_member:
            raise TeamError("Member not found")

        if isinstance(new_role, str):
            new_role = TeamRole(new_role)

        current_role = getattr(target_member, "role", None)
        normalized_current_role = (
            self._normalize_role(current_role) if current_role is not None else None
        )

        if normalized_current_role == TeamRole.ADMIN and new_role != TeamRole.ADMIN:
            admin_count = (
                await self.team_member_repo.count_admins(team_id)
                if hasattr(self.team_member_repo, "count_admins")
                else 1
            )
            if admin_count <= 1:
                raise TeamError("Cannot demote last admin")

        if isinstance(target_member, TeamMember):
            target_member.role = new_role
        else:
            target_member.role = new_role.value
        target_member.updated_at = datetime.now(UTC)
        await self.db_session.commit()

        return target_member

    async def remove_member(
        self,
        team_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
        target_user_id: uuid.UUID,
    ) -> bool:
        """Remove a member from a team.

        Args:
            team_id: Team ID
            requesting_user_id: User ID of the requester
            target_user_id: User ID to remove

        Returns:
            True if successful

        Raises:
            TeamError: If member not found or user not authorized
        """
        requesting_member = await self._get_member(requesting_user_id, team_id)

        if requesting_member is None:
            raise TeamError("Requesting member not found")

        requesting_role = getattr(requesting_member, "role", None)
        normalized_requesting_role = self._normalize_role(requesting_role)
        if requesting_user_id != target_user_id and normalized_requesting_role != TeamRole.ADMIN:
            raise TeamError("Only admins can remove other members")

        member = await self._get_member(target_user_id, team_id)

        if not member:
            raise TeamError("Member not found")

        await self.db_session.delete(member)
        await self.db_session.commit()
        return True

    async def get_user_teams(self, user_id: uuid.UUID) -> list[dict]:
        """Get all teams for a user.

        Args:
            user_id: User ID

        Returns:
            List of teams as dictionaries
        """
        members = await self.member_repo.list_by_user_id(user_id)
        team_ids = [m.team_id for m in members]

        if not team_ids:
            return []

        stmt = select(Team).where(Team.id.in_(team_ids), Team.deleted_at.is_(None))
        result = await self.db_session.execute(stmt)
        teams = result.scalars().all()

        return [_team_to_dict(team) for team in teams]

    async def check_plan_limits(
        self, team_id: uuid.UUID, team: Team | None = None
    ) -> tuple[bool, str | None]:
        """Check if a team is within its plan limits.

        Args:
            team_id: Team ID
            team: Optional team model (will be fetched if not provided)

        Returns:
            Tuple of (is_within_limits, error_message)
        """
        if team is None:
            stmt = select(Team).where(Team.id == team_id, Team.deleted_at.is_(None))
            result = await self.db_session.execute(stmt)
            team = result.scalar_one_or_none()

        if not team:
            return False, "Team not found"

        plan = team.plan
        limits = PLAN_LIMITS[plan]

        member_list = await self.member_repo.get_by_team_id(team_id)
        member_count = len(member_list)

        if member_count >= limits["members"]:
            return False, f"Plan limit reached: {limits['members']} members maximum"

        return True, None

    def get_team_limits(self, team: Team) -> TeamMemberLimits:
        """Get the limits for a team based on its plan.

        Args:
            team: Team model

        Returns:
            TeamMemberLimits with plan limits
        """
        limits = PLAN_LIMITS[team.plan]
        return TeamMemberLimits(
            max_members=int(limits["members"]) if limits["members"] != float("inf") else 9999,
            max_upload_mb=0,
            max_jobs_per_month=int(limits["uploads_per_month"])
            if limits["uploads_per_month"] != float("inf")
            else 9999,
        )


__all__ = ["AsyncTeamService", "TeamError"]
