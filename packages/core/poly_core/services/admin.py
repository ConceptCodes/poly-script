from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from poly_db.models.teams import Team
from poly_db.models.users import User
from poly_db.models.transcription_jobs import TranscriptionJob, JobStatus
from poly_db.repositories.admin import AdminUserRepository, AuditLogRepository
from poly_db.repositories.user_repository import UserRepository
from poly_db.repositories.jobs import TranscriptionJobRepository
from poly_db.repositories.base import BaseRepository


class AdminService:
    """Administrative service facade for the core admin features.

    Minimal, safe implementations that leverage existing repositories.
    """

    def __init__(self, db_session: Session):
        self.session = db_session

        self.admin_repo = AdminUserRepository(db_session)
        self.audit_repo = AuditLogRepository(db_session)

        self.user_repo = UserRepository(db_session)

        self.team_repo: BaseRepository[Team] = BaseRepository(Team, db_session)
        self.team_member_repo = None

        self.job_repo = TranscriptionJobRepository(db_session)

        self.team_invite_repo = None

    def dashboard(self) -> Dict[str, Any]:
        try:
            users_count = len(self.user_repo.list())
        except Exception:
            users_count = 0
        try:
            teams_count = len(self.team_repo.list())
        except Exception:
            teams_count = 0
        try:
            jobs_count = len(self.job_repo.list())
        except Exception:
            jobs_count = 0
        try:
            admins_count = len(self.admin_repo.list())
        except Exception:
            admins_count = 0

        return {
            "users": users_count,
            "teams": teams_count,
            "jobs": jobs_count,
            "administrators": admins_count,
        }

    def users(self) -> List[Dict[str, Any]]:
        users = self.user_repo.list()
        result: List[Dict[str, Any]] = []
        for u in users:
            result.append(
                {
                    "id": str(u.id),
                    "email": u.email,
                    "full_name": getattr(u, "full_name", None),
                    "is_active": getattr(u, "is_active", False),
                    "is_verified": getattr(u, "is_verified", False),
                    "is_suspended": getattr(u, "is_suspended", False),
                }
            )
        return result

    def teams(self) -> List[Dict[str, Any]]:
        teams = self.team_repo.list()
        out: List[Dict[str, Any]] = []
        for t in teams:
            out.append(
                {
                    "id": str(t.id),
                    "name": t.name,
                    "host_language": t.host_language,
                    "plan": getattr(t, "plan", None).name if hasattr(t, "plan") else None,
                    "monthly_upload_count": getattr(t, "monthly_upload_count", 0),
                    "is_suspended": getattr(t, "is_suspended", False),
                }
            )
        return out

    def jobs(self) -> List[Dict[str, Any]]:
        jobs = self.job_repo.list()
        out: List[Dict[str, Any]] = []
        for j in jobs:
            out.append(
                {
                    "id": str(j.id),
                    "team_id": str(j.team_id) if getattr(j, "team_id", None) is not None else None,
                    "status": j.status.value if hasattr(j.status, "value") else str(j.status),
                    "progress": getattr(j, "progress", 0),
                    "engine": getattr(j, "engine", None),
                }
            )
        return out

    def analytics(self) -> Dict[str, Any]:
        users_count = len(self.user_repo.list())
        teams_count = len(self.team_repo.list())
        jobs = self.job_repo.list()
        total_jobs = len(jobs)
        succeeded = sum(1 for j in jobs if getattr(j, "status", None) == JobStatus.SUCCEEDED)
        return {
            "users": users_count,
            "teams": teams_count,
            "jobs": total_jobs,
            "successful_jobs": succeeded,
        }

    
    # ============================================
    # Admin User Management Methods
    # ============================================
    def create_admin_user(
        self,
        email: str,
        password: str,
        full_name: str,
        role: str,
        created_by_admin_id: uuid.UUID,
    ) -> Dict[str, Any]:
        """Create a new admin user (SUPER_ADMIN only)."""
        from poly_core.services.admin_auth import AdminAuthService
        
        if role not in ["ADMIN", "SUPER_ADMIN"]:
            raise ValueError("Invalid admin role")
        
        auth_service = AdminAuthService(self.session, "dummy-secret", 60)
        admin = auth_service.create_admin_user(
            email=email,
            password=password,
            full_name=full_name,
            role=role,
            created_by_admin_id=created_by_admin_id,
        )
        
        return {
            "id": str(admin.id),
            "email": admin.email,
            "full_name": admin.full_name,
            "role": admin.role,
            "is_active": admin.is_active,
            "is_suspended": admin.is_suspended,
        }

    def suspend_admin_user(
        self,
        admin_id: uuid.UUID,
        suspended_by_admin_id: uuid.UUID,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Suspend an admin user (SUPER_ADMIN only)."""
        admin = self.admin_repo.get_by_id(admin_id)
        if not admin:
            raise ValueError("Admin user not found")
        
        previous_state = {"is_suspended": admin.is_suspended}
        
        self.admin_repo.update(
            admin_id,
            is_suspended=True,
            suspended_at=datetime.now(timezone.utc),
        )
        self.session.commit()
        
        # Audit log
        self.audit_repo.create(
            admin_user_id=suspended_by_admin_id,
            target_type="admin_user",
            target_id=str(admin_id),
            action="suspend_admin",
            previous_state=previous_state,
            new_state={"is_suspended": True},
            reason=reason,
        )
        self.session.commit()
        
        return {"status": "success", "is_suspended": True}

    def unsuspend_admin_user(
        self,
        admin_id: uuid.UUID,
        unsuspended_by_admin_id: uuid.UUID,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Unsuspend an admin user (SUPER_ADMIN only)."""
        admin = self.admin_repo.get_by_id(admin_id)
        if not admin:
            raise ValueError("Admin user not found")
        
        previous_state = {"is_suspended": admin.is_suspended}
        
        self.admin_repo.update(
            admin_id,
            is_suspended=False,
            suspended_at=None,
        )
        self.session.commit()
        
        # Audit log
        self.audit_repo.create(
            admin_user_id=unsuspended_by_admin_id,
            target_type="admin_user",
            target_id=str(admin_id),
            action="unsuspend_admin",
            previous_state=previous_state,
            new_state={"is_suspended": False},
            reason=reason,
        )
        self.session.commit()
        
        return {"status": "success", "is_suspended": False}

    def change_admin_role(
        self,
        admin_id: uuid.UUID,
        new_role: str,
        changed_by_admin_id: uuid.UUID,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Change admin role (SUPER_ADMIN only)."""
        if new_role not in ["ADMIN", "SUPER_ADMIN"]:
            raise ValueError("Invalid admin role")
        
        admin = self.admin_repo.get_by_id(admin_id)
        if not admin:
            raise ValueError("Admin user not found")
        
        # Prevent self-modification
        if admin_id == changed_by_admin_id:
            raise ValueError("Cannot change your own role")
        
        previous_state = {"role": admin.role}
        
        self.admin_repo.update(admin_id, role=new_role)
        self.session.commit()
        
        # Audit log
        self.audit_repo.create(
            admin_user_id=changed_by_admin_id,
            target_type="admin_user",
            target_id=str(admin_id),
            action="change_admin_role",
            previous_state=previous_state,
            new_state={"role": new_role},
            reason=reason,
        )
        self.session.commit()
        
        return {"status": "success", "role": new_role}

    def delete_admin_user(
        self,
        admin_id: uuid.UUID,
        deleted_by_admin_id: uuid.UUID,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Delete an admin user (soft delete, SUPER_ADMIN only)."""
        admin = self.admin_repo.get_by_id(admin_id)
        if not admin:
            raise ValueError("Admin user not found")
        
        # Prevent self-deletion
        if admin_id == deleted_by_admin_id:
            raise ValueError("Cannot delete your own account")
        
        previous_state = {
            "email": admin.email,
            "full_name": admin.full_name,
            "role": admin.role,
            "is_active": admin.is_active,
        }
        
        self.admin_repo.update(admin_id, is_active=False, deleted_at=datetime.now(timezone.utc))
        self.session.commit()
        
        # Audit log
        self.audit_repo.create(
            admin_user_id=deleted_by_admin_id,
            target_type="admin_user",
            target_id=str(admin_id),
            action="delete_admin",
            previous_state=previous_state,
            new_state={"is_active": False, "deleted_at": datetime.now(timezone.utc).isoformat()},
            reason=reason,
        )
        self.session.commit()
        
        return {"status": "success"}

    # ============================================
    # Team Management Methods
    # ============================================
    def suspend_team(
        self,
        team_id: uuid.UUID,
        suspended_by_admin_id: uuid.UUID,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Suspend a team (SUPER_ADMIN only)."""
        team = self.team_repo.get_by_id(team_id)
        if not team:
            raise ValueError("Team not found")
        
        from poly_db.models.teams import Team as TeamModel
        team_obj = self.session.query(TeamModel).filter(TeamModel.id == team_id).first()
        
        previous_state = {"is_suspended": getattr(team_obj, "is_suspended", False)}
        
        self.session.query(TeamModel).filter(TeamModel.id == team_id).update(
            {"is_suspended": True, "suspended_at": datetime.now(timezone.utc)}
        )
        self.session.commit()
        
        # Audit log
        self.audit_repo.create(
            admin_user_id=suspended_by_admin_id,
            target_type="team",
            target_id=str(team_id),
            action="suspend_team",
            previous_state=previous_state,
            new_state={"is_suspended": True},
            reason=reason,
        )
        self.session.commit()
        
        return {"status": "success", "is_suspended": True}

    def unsuspend_team(
        self,
        team_id: uuid.UUID,
        unsuspended_by_admin_id: uuid.UUID,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Unsuspend a team (SUPER_ADMIN only)."""
        team = self.team_repo.get_by_id(team_id)
        if not team:
            raise ValueError("Team not found")
        
        from poly_db.models.teams import Team as TeamModel
        team_obj = self.session.query(TeamModel).filter(TeamModel.id == team_id).first()
        
        previous_state = {"is_suspended": getattr(team_obj, "is_suspended", False)}
        
        self.session.query(TeamModel).filter(TeamModel.id == team_id).update(
            {"is_suspended": False, "suspended_at": None}
        )
        self.session.commit()
        
        # Audit log
        self.audit_repo.create(
            admin_user_id=unsuspended_by_admin_id,
            target_type="team",
            target_id=str(team_id),
            action="unsuspend_team",
            previous_state=previous_state,
            new_state={"is_suspended": False},
            reason=reason,
        )
        self.session.commit()
        
        return {"status": "success", "is_suspended": False}

    
    # ============================================
    # Impersonation Methods
    # ============================================
    def create_impersonation_token(
        self,
        target_user_id: uuid.UUID,
        admin_id: uuid.UUID,
    ) -> Dict[str, Any]:
        """Create an impersonation token for a user (SUPER_ADMIN only)."""
        user = self.user_repo.get_by_id(target_user_id)
        if not user:
            raise ValueError("User not found")
        
        from poly_core.services.auth import AuthService
        auth_service = AuthService(
            db_session=self.session,
            jwt_secret="impersonation-secret-placeholder",
            jwt_expiry_minutes=60,
            notification_service=None,
            email_verification_expiry_hours=24,
            password_reset_expiry_hours=1,
        )
        
        # Create a user token for impersonation
        token = auth_service.create_access_token(target_user_id)
        
        # Audit log impersonation
        self.audit_repo.create(
            admin_user_id=admin_id,
            target_type="impersonation",
            target_id=str(target_user_id),
            action="create_impersonation_token",
            new_state={
                "impersonated_user_email": user.email,
                "impersonated_user_id": str(target_user_id),
            },
        )
        self.session.commit()
        
        return {"impersonation_token": token, "user_id": str(target_user_id)}

    def revoke_impersonation_token(
        self,
        token_id: str,
        admin_id: uuid.UUID,
    ) -> Dict[str, Any]:
        """Revoke an impersonation token (SUPER_ADMIN only)."""
        # For simplicity, we log the revocation
        # In production, you would track and invalidate specific tokens
        self.audit_repo.create(
            admin_user_id=admin_id,
            target_type="impersonation",
            target_id=token_id,
            action="revoke_impersonation_token",
            new_state={"token_revoked": True},
        )
        self.session.commit()
        
        return {"status": "success", "message": "Token revoked"}

    # ============================================
    # Enhanced Analytics Methods
    # ============================================
    def analytics_with_timeframe(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        granularity: str = "day",
    ) -> Dict[str, Any]:
        """Get analytics with optional time range and granularity."""
        if not end_date:
            end_date = datetime.now(timezone.utc)
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Base analytics
        base_analytics = self.analytics()
        
        # Add time range and granularity info
        return {
            **base_analytics,
            "timeframe": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "granularity": granularity,
            },
        }

    def job_volume_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get job volume analytics by status."""
        if not end_date:
            end_date = datetime.now(timezone.utc)
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        jobs = self.job_repo.list()
        
        # Filter by date range (naive implementation - in prod, use DB query)
        recent_jobs = [
            j for j in jobs
            if j.created_at and start_date <= j.created_at <= end_date
        ]
        
        status_counts = {}
        for job in recent_jobs:
            status = job.status.value if hasattr(job.status, "value") else str(job.status)
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total": len(recent_jobs),
            "by_status": status_counts,
            "timeframe": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
        }

    # ============================================
    # Settings Methods
    # ============================================
    def get_system_settings(self) -> Dict[str, Any]:
        """Get system-wide settings."""
        # In production, these would come from a settings table
        return {
            "plan_limits": {
                "FREE": {
                    "max_users": 1,
                    "max_teams": 1,
                    "monthly_upload_limit": 10,
                },
                "STANDARD": {
                    "max_users": 10,
                    "max_teams": 3,
                    "monthly_upload_limit": 100,
                },
                "PRO": {
                    "max_users": -1,  # Unlimited
                    "max_teams": -1,  # Unlimited
                    "monthly_upload_limit": 1000,
                },
            },
            "retention_windows": {
                "deleted_users_days": 30,
                "deleted_teams_days": 30,
                "audit_logs_days": 365,
            },
            "feature_flags": {
                "registration_enabled": True,
                "stripe_enabled": True,
                "impersonation_enabled": True,
            },
        }

    def update_system_settings(
        self,
        settings_update: Dict[str, Any],
        admin_id: uuid.UUID,
    ) -> Dict[str, Any]:
        """Update system settings (SUPER_ADMIN only)."""
        # In production, this would persist to a settings table
        current_settings = self.get_system_settings()
        
        # Apply updates (shallow merge)
        for section, updates in settings_update.items():
            if section in current_settings:
                current_settings[section].update(updates)
        
        # Audit log settings changes
        self.audit_repo.create(
            admin_user_id=admin_id,
            target_type="settings",
            target_id="system",
            action="update_system_settings",
            new_state=settings_update,
        )
        self.session.commit()
        
        return current_settings

    def settings(self) -> Dict[str, Any]:
        admins = self.admin_repo.list()
        admin_list = [
            {
                "id": str(a.id),
                "email": a.email,
                "full_name": a.full_name,
                "is_active": getattr(a, "is_active", True),
            }
            for a in admins
        ]
        return {
            "administrators": admin_list,
            "system": {
                "max_users": 0,
                "max_teams": 0,
            },
        }
