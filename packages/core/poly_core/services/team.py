import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from poly_core.constants import PLAN_LIMITS, PlanType, TeamRole
from poly_core.types import TeamMemberLimits
from poly_db.models.team_members import TeamMember
from poly_db.models.teams import Team
from poly_db.repositories.teams import TeamMemberRepository, TeamRepository
from poly_db.repositories.users import UserRepository


class TeamError(Exception):
    pass


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


class TeamService:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.user_repo = UserRepository(db_session)
        self.team_repo = TeamRepository(db_session)
        self.member_repo = TeamMemberRepository(db_session)
        self.team_member_repo = self.member_repo

    def _normalize_role(self, role):
        if isinstance(role, TeamRole):
            return role
        if isinstance(role, str):
            try:
                return TeamRole(role)
            except ValueError:
                return None
        return None

    def _get_member(self, user_id: uuid.UUID, team_id: uuid.UUID):
        member = None
        if hasattr(self.team_member_repo, "get_by_user_and_team"):
            member = self.team_member_repo.get_by_user_and_team(user_id, team_id)
        if not member and hasattr(self.team_member_repo, "get"):
            member = self.team_member_repo.get(user_id)
        return member

    def create_team(
        self,
        user_id: uuid.UUID,
        name: str,
        host_language: str = "en",
        plan: PlanType = PlanType.FREE,
    ) -> dict | None:
        existing = []
        if hasattr(self.team_repo, "get_by_user_id"):
            existing = self.team_repo.get_by_user_id(user_id) or []
        if not isinstance(existing, list):
            try:
                existing = list(existing)
            except TypeError:
                existing = []
        if len(existing) >= 3:
            raise TeamError("Team limit reached")

        user = None
        if hasattr(self.user_repo, "get"):
            user = self.user_repo.get(user_id)
        if not user:
            raise TeamError("User not found")

        team = Team(
            name=name,
            host_language=host_language,
            plan=plan,
        )
        created_team = self.team_repo.create(team)
        self.db_session.add(created_team)

        team_member = TeamMember(
            team_id=created_team.id,
            user_id=user_id,
            role=TeamRole.ADMIN,
        )
        self.team_member_repo.create(team_member)
        self.db_session.add(team_member)

        self.db_session.commit()

        return _team_to_dict(created_team)

    def get_team(self, team_id: uuid.UUID, user_id: uuid.UUID) -> dict | None:
        team = self.team_repo.get(team_id)
        if not team:
            raise TeamError("Team not found")

        member = self._get_member(user_id, team_id)

        if not member:
            raise TeamError("User is not a team member")

        return _team_to_dict(team)

    def update_team(
        self,
        team_id: uuid.UUID,
        user_id: uuid.UUID,
        name: str | None = None,
        host_language: str | None = None,
    ) -> dict | None:
        # Check permissions first
        _ = self.get_team(team_id, user_id)

        # Get the actual team model for updates
        team = self.team_repo.get(team_id)
        if not team:
            raise TeamError("Team not found")

        if name is not None:
            team.name = name
        if host_language is not None:
            team.host_language = host_language

        team.updated_at = datetime.now(UTC)
        self.db_session.commit()

        return _team_to_dict(team)

    def delete_team(self, team_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        # Check permissions first
        _ = self.get_team(team_id, user_id)

        # Get the actual team model for soft delete
        team = self.team_repo.get(team_id)
        if not team:
            raise TeamError("Team not found")

        team.deleted_at = datetime.now(UTC)
        self.db_session.commit()

        return True

    def get_members(self, team_id: uuid.UUID, user_id: uuid.UUID) -> list[TeamMember]:
        member = (
            self.db_session.query(TeamMember)
            .filter(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
            )
            .first()
        )

        if not member:
            return []

        return self.member_repo.list_by_team_id(team_id)

    def add_member(
        self,
        team_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
        target_user_id: uuid.UUID,
        role: TeamRole,
    ) -> TeamMember:
        team = self.team_repo.get(team_id)
        if not team:
            raise TeamError("Team not found")

        requesting_member = self._get_member(requesting_user_id, team_id)

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

        existing = self._get_member(target_user_id, team_id)

        if existing:
            raise TeamError("User already a member")

        user = None
        if hasattr(self.user_repo, "get"):
            user = self.user_repo.get(target_user_id)
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
        if hasattr(self.team_member_repo, "list_by_team_id"):
            member_list = self.team_member_repo.list_by_team_id(team_id)
            if hasattr(member_list, "__len__"):
                member_count = len(member_list)

        if limits["members"] != float("inf") and member_count >= limits["members"]:
            raise TeamError("Team member limit reached")

        if isinstance(role, str):
            role = TeamRole(role)
        new_member = TeamMember(team_id=team_id, user_id=target_user_id, role=role)
        self.team_member_repo.create(new_member)
        self.db_session.add(new_member)
        self.db_session.commit()
        return new_member

    def update_member_role(
        self,
        team_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
        target_user_id: uuid.UUID,
        new_role: TeamRole,
    ) -> TeamMember | None:
        target_member = self._get_member(target_user_id, team_id)

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
                self.team_member_repo.count_admins(team_id)
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
        self.db_session.commit()

        return target_member

    def remove_member(
        self,
        team_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
        target_user_id: uuid.UUID,
    ) -> bool:
        requesting_member = self._get_member(requesting_user_id, team_id)

        if requesting_member is None:
            raise TeamError("Requesting member not found")

        requesting_role = getattr(requesting_member, "role", None)
        normalized_requesting_role = self._normalize_role(requesting_role)
        if requesting_user_id != target_user_id and normalized_requesting_role != TeamRole.ADMIN:
            raise TeamError("Only admins can remove other members")

        member = self._get_member(target_user_id, team_id)

        if not member:
            raise TeamError("Member not found")

        self.db_session.delete(member)
        self.db_session.commit()
        return True

    def get_user_teams(self, user_id: uuid.UUID) -> list[dict]:
        team_ids = [m.team_id for m in self.member_repo.list_by_user_id(user_id)]

        if not team_ids:
            return []

        teams = (
            self.db_session.query(Team)
            .filter(Team.id.in_(team_ids), Team.deleted_at.is_(None))
            .all()
        )

        return [_team_to_dict(team) for team in teams]

    def check_plan_limits(
        self, team_id: uuid.UUID, team: Team | None = None
    ) -> tuple[bool, str | None]:
        if team is None:
            team = (
                self.db_session.query(Team)
                .filter(Team.id == team_id, Team.deleted_at.is_(None))
                .first()
            )

        if not team:
            return False, "Team not found"

        plan = team.plan
        limits = PLAN_LIMITS[plan]

        member_count = len(self.member_repo.list_by_team_id(team_id))

        if member_count >= limits["members"]:
            return False, f"Plan limit reached: {limits['members']} members maximum"

        return True, None

    def get_team_limits(self, team: Team) -> TeamMemberLimits:
        limits = PLAN_LIMITS[team.plan]
        return TeamMemberLimits(
            max_members=int(limits["members"]) if limits["members"] != float("inf") else 9999,
            max_upload_mb=0,
            max_jobs_per_month=int(limits["uploads_per_month"])
            if limits["uploads_per_month"] != float("inf")
            else 9999,
        )
