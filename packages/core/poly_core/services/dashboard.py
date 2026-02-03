import uuid
from datetime import UTC, datetime
from typing import Any, ClassVar

from sqlalchemy.orm import Session

from poly_core.constants import PLAN_LIMITS, JobState
from poly_db.models.team_members import TeamMember
from poly_db.models.teams import Team
from poly_db.repositories.jobs import JobRepository
from poly_db.repositories.teams import TeamMemberRepository, TeamRepository
from poly_db.repositories.users import UserRepository


class ActivityRegistry:
    """Registry for team activity events."""

    EVENT_TYPES: ClassVar[dict[str, dict[str, str]]] = {
        "job_created": {"display_name": "Job Created", "icon": "upload"},
        "job_completed": {"display_name": "Job Completed", "icon": "check"},
        "job_failed": {"display_name": "Job Failed", "icon": "alert"},
        "team_joined": {"display_name": "Team Joined", "icon": "users"},
        "member_invited": {"display_name": "Member Invited", "icon": "mail"},
        "plan_changed": {"display_name": "Plan Changed", "icon": "credit-card"},
        "credits_purchased": {"display_name": "Credits Purchased", "icon": "plus"},
        "transcript_edited": {"display_name": "Transcript Edited", "icon": "edit"},
        "export_downloaded": {"display_name": "Export Downloaded", "icon": "download"},
    }

    @classmethod
    def register_event_type(cls, event_type: str, display_name: str, icon: str):
        """Register a new activity event type."""
        cls.EVENT_TYPES[event_type] = {"display_name": display_name, "icon": icon}

    @classmethod
    def get_event_type_info(cls, event_type: str) -> dict[str, str] | None:
        """Get info for an event type."""
        return cls.EVENT_TYPES.get(event_type)


class DashboardService:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.user_repo = UserRepository(db_session)
        self.team_repo = TeamRepository(db_session)
        self.member_repo = TeamMemberRepository(db_session)
        self.job_repo = JobRepository(db_session)

    def get_dashboard_stats(self, team_id: uuid.UUID, user_id: uuid.UUID) -> dict[str, Any]:
        """Get dashboard statistics for a team."""
        team = self._get_team_access(team_id, user_id)
        if not team:
            raise ValueError("Access denied")

        plan_limits = PLAN_LIMITS[team.plan]

        jobs = self.job_repo.list_by_team_id(team_id)

        total_jobs = len(jobs)
        succeeded_jobs = len([j for j in jobs if j.state == JobState.SUCCEEDED])
        failed_jobs = len([j for j in jobs if j.state == JobState.FAILED])

        members = self.member_repo.list_by_team_id(team_id)
        member_count = len(members)

        return {
            "total_jobs": total_jobs,
            "succeeded_jobs": succeeded_jobs,
            "failed_jobs": failed_jobs,
            "member_count": member_count,
            "plan": team.plan.value,
            "credits_balance": team.credits_balance or 0,
            "max_members": plan_limits["members"]
            if plan_limits["members"] != float("inf")
            else None,
            "max_jobs_per_month": plan_limits["uploads_per_month"]
            if plan_limits["uploads_per_month"] != float("inf")
            else None,
        }

    def get_recent_jobs(
        self, team_id: uuid.UUID, user_id: uuid.UUID, limit: int = 10
    ) -> list[dict[str, Any]]:
        """Get recent jobs for a team."""
        team = self._get_team_access(team_id, user_id)
        if not team:
            raise ValueError("Access denied")

        jobs = self.job_repo.list_by_team_id(team_id)
        jobs_sorted = sorted(jobs, key=lambda j: j.created_at, reverse=True)
        recent_jobs = jobs_sorted[:limit]

        return [
            {
                "id": job.id,
                "file_name": job.file_name,
                "state": job.state.value,
                "created_at": job.created_at.isoformat(),
                "language": job.language,
                "duration_seconds": job.duration_seconds,
            }
            for job in recent_jobs
        ]

    def get_team_activity(
        self, team_id: uuid.UUID, user_id: uuid.UUID, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Get team activity feed."""
        team = self._get_team_access(team_id, user_id)
        if not team:
            raise ValueError("Access denied")

        activities = []

        # Job activities
        jobs = self.job_repo.list_by_team_id(team_id)
        for job in jobs:
            if job.state == JobState.SUCCEEDED:
                activities.append(
                    {
                        "type": "job_completed",
                        "display_name": ActivityRegistry.EVENT_TYPES["job_completed"][
                            "display_name"
                        ],
                        "icon": ActivityRegistry.EVENT_TYPES["job_completed"]["icon"],
                        "message": f"Completed job: {job.file_name}",
                        "timestamp": job.updated_at.isoformat()
                        if job.updated_at
                        else job.created_at.isoformat(),
                    }
                )
            elif job.state == JobState.FAILED:
                activities.append(
                    {
                        "type": "job_failed",
                        "display_name": ActivityRegistry.EVENT_TYPES["job_failed"]["display_name"],
                        "icon": ActivityRegistry.EVENT_TYPES["job_failed"]["icon"],
                        "message": f"Failed job: {job.file_name}",
                        "timestamp": job.updated_at.isoformat()
                        if job.updated_at
                        else job.created_at.isoformat(),
                    }
                )
            else:
                activities.append(
                    {
                        "type": "job_created",
                        "display_name": ActivityRegistry.EVENT_TYPES["job_created"]["display_name"],
                        "icon": ActivityRegistry.EVENT_TYPES["job_created"]["icon"],
                        "message": f"Created job: {job.file_name}",
                        "timestamp": job.created_at.isoformat(),
                    }
                )

        # Team member activities
        members = self.member_repo.list_by_team_id(team_id)
        for member in members:
            activities.append(
                {
                    "type": "team_joined",
                    "display_name": ActivityRegistry.EVENT_TYPES["team_joined"]["display_name"],
                    "icon": ActivityRegistry.EVENT_TYPES["team_joined"]["icon"],
                    "message": f"Member joined: {member.user.full_name or member.user.email}",
                    "timestamp": member.created_at.isoformat(),
                }
            )

        # Sort by timestamp (most recent first)
        activities_sorted = sorted(activities, key=lambda a: a["timestamp"], reverse=True)

        return activities_sorted[:limit]

    def get_usage_this_month(self, team_id: uuid.UUID, user_id: uuid.UUID) -> dict[str, Any]:
        """Get usage statistics for the current month."""
        team = self._get_team_access(team_id, user_id)
        if not team:
            raise ValueError("Access denied")

        now = datetime.now(UTC)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        jobs = self.job_repo.list_by_team_id(team_id)
        jobs_this_month = [j for j in jobs if j.created_at >= month_start]

        return {
            "jobs_created": len(jobs_this_month),
            "jobs_succeeded": len([j for j in jobs_this_month if j.state == JobState.SUCCEEDED]),
            "jobs_failed": len([j for j in jobs_this_month if j.state == JobState.FAILED]),
            "month_start": month_start.isoformat(),
        }

    def _get_team_access(self, team_id: uuid.UUID, user_id: uuid.UUID) -> Team | None:
        """Check if user has access to team and return team if yes."""
        member = (
            self.db_session.query(TeamMember)
            .filter(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
            )
            .first()
        )

        if not member:
            return None

        return self.db_session.query(Team).filter(Team.id == team_id).first()
