from typing import Optional
import uuid
import secrets
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from poly_db.repositories.teams import TeamRepository, TeamMemberRepository
from poly_db.models.teams import Team
from poly_db.models.team_members import TeamMember
from poly_db.models.users import User

from ..constants import TeamRole, PlanType, PLAN_LIMITS
from ..types import TeamMemberLimits


class TeamService:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.team_repo = TeamRepository(db_session)
        self.member_repo = TeamMemberRepository(db_session)

    def create_team(
        self,
        user_id: uuid.UUID,
        name: str,
        host_language: str = "en",
        plan: PlanType = PlanType.FREE,
    ) -> Optional[Team]:
        user = self.db_session.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        team = Team(
            name=name,
            host_language=host_language,
            plan=plan,
        )
        self.team_repo.create(team)

        team_member = TeamMember(
            team_id=team.id,
            user_id=user_id,
            role=TeamRole.ADMIN,
        )
        self.member_repo.create(team_member)

        return team

    def get_team(self, team_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Team]:
        member = self.db_session.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id,
        ).first()

        if not member:
            return None

        return self.db_session.query(Team).filter(Team.id == team_id).first()

    def update_team(
        self,
        team_id: uuid.UUID,
        user_id: uuid.UUID,
        name: Optional[str] = None,
        host_language: Optional[str] = None,
    ) -> Optional[Team]:
        team = self.get_team(team_id, user_id)
        if not team:
            return None

        member = self.db_session.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id,
        ).first()

        if not member or member.role != TeamRole.ADMIN:
            return None

        if name is not None:
            team.name = name
        if host_language is not None:
            team.host_language = host_language

        team.updated_at = datetime.now(timezone.utc)
        self.db_session.commit()

        return team

    def delete_team(self, team_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        team = self.get_team(team_id, user_id)
        if not team:
            return False

        member = self.db_session.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id,
        ).first()

        if not member or member.role != TeamRole.ADMIN:
            return False

        team.deleted_at = datetime.now(timezone.utc)
        self.db_session.commit()

        return True

    def get_members(
        self, team_id: uuid.UUID, user_id: uuid.UUID
    ) -> list[TeamMember]:
        member = self.db_session.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id,
        ).first()

        if not member:
            return []

        return self.member_repo.list_by_team_id(team_id)

    def update_member_role(
        self,
        team_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
        target_user_id: uuid.UUID,
        new_role: TeamRole,
    ) -> Optional[TeamMember]:
        requesting_member = self.db_session.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == requesting_user_id,
        ).first()

        if not requesting_member or requesting_member.role != TeamRole.ADMIN:
            return None

        if requesting_user_id == target_user_id:
            return None

        target_member = self.db_session.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == target_user_id,
        ).first()

        if not target_member:
            return None

        target_member.role = new_role
        target_member.updated_at = datetime.now(timezone.utc)
        self.db_session.commit()

        return target_member

    def remove_member(
        self,
        team_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
        target_user_id: uuid.UUID,
    ) -> bool:
        requesting_member = self.db_session.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == requesting_user_id,
        ).first()

        if not requesting_member:
            return False

        if requesting_user_id == target_user_id:
            member = requesting_member
        else:
            if requesting_member.role != TeamRole.ADMIN:
                return False

            member = self.db_session.query(TeamMember).filter(
                TeamMember.team_id == team_id,
                TeamMember.user_id == target_user_id,
            ).first()

        if not member:
            return False

        self.member_repo.delete(member.id)
        return True

    def get_user_teams(self, user_id: uuid.UUID) -> list[Team]:
        team_ids = [
            m.team_id for m in self.member_repo.list_by_user_id(user_id)
        ]

        if not team_ids:
            return []

        return self.db_session.query(Team).filter(
            Team.id.in_(team_ids), Team.deleted_at.is_(None)
        ).all()

    def check_plan_limits(
        self, team_id: uuid.UUID, team: Optional[Team] = None
    ) -> tuple[bool, Optional[str]]:
        if team is None:
            team = self.db_session.query(Team).filter(
                Team.id == team_id, Team.deleted_at.is_(None)
            ).first()

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
            max_jobs_per_month=int(limits["uploads_per_month"]) if limits["uploads_per_month"] != float("inf") else 9999,
        )
