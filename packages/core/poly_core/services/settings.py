from typing import Optional, List
from datetime import datetime, timezone
import uuid
from sqlalchemy.orm import Session

from poly_db.repositories.users import UserRepository
from poly_db.repositories.teams import TeamRepository, TeamMemberRepository
from poly_db.models.users import User
from poly_db.models.teams import Team
from poly_db.models.team_members import TeamMember

from ..constants import TeamRole, PlanType
from ..services.auth import AuthService


class SettingsService:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.user_repo = UserRepository(db_session)
        self.team_repo = TeamRepository(db_session)
        self.member_repo = TeamMemberRepository(db_session)
    
    def get_user_settings(self, user_id: uuid.UUID) -> dict:
        """Get user profile and settings."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_verified": user.is_verified,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
        }
    
    def update_user_profile(
        self,
        user_id: uuid.UUID,
        full_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> User:
        """Update user profile."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        if full_name is not None:
            user.full_name = full_name
        if avatar_url is not None:
            user.avatar_url = avatar_url
        
        user.updated_at = datetime.now(timezone.utc)
        return self.user_repo.update(user)
    
    def update_user_email(
        self,
        user_id: uuid.UUID,
        new_email: str,
        auth_service: AuthService,
    ) -> User:
        """Update user email (requires re-verification)."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Check if email is already taken
        existing = self.user_repo.get_by_email(new_email)
        if existing and existing.id != user_id:
            raise ValueError("Email already exists")
        
        user.email = new_email
        user.is_verified = False  # Require re-verification
        user.updated_at = datetime.now(timezone.utc)
        
        updated_user = self.user_repo.update(user)
        
        # Generate new verification token
        auth_service.generate_verification_token(user_id)
        
        return updated_user
    
    def update_user_password(
        self,
        user_id: uuid.UUID,
        current_password: str,
        new_password: str,
        auth_service: AuthService,
    ) -> User:
        """Update user password."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        if not auth_service.verify_password(current_password, user.hashed_password):
            raise ValueError("Current password is incorrect")
        
        user.hashed_password = auth_service.hash_password(new_password)
        user.updated_at = datetime.now(timezone.utc)
        
        return self.user_repo.update(user)
    
    def get_team_settings(self, team_id: uuid.UUID, user_id: uuid.UUID) -> dict:
        """Get team settings."""
        team = self._get_team_with_access(team_id, user_id)
        if not team:
            raise ValueError("Access denied")
        
        members = self.member_repo.list_by_team_id(team_id)
        
        return {
            "id": team.id,
            "name": team.name,
            "host_language": team.host_language,
            "plan": team.plan.value,
            "credits_balance": team.credits_balance or 0,
            "created_at": team.created_at.isoformat(),
            "members_count": len(members),
        }
    
    def update_team_settings(
        self,
        team_id: uuid.UUID,
        user_id: uuid.UUID,
        name: Optional[str] = None,
        host_language: Optional[str] = None,
    ) -> Team:
        """Update team settings."""
        team = self._get_team_with_access(team_id, user_id)
        if not team:
            raise ValueError("Access denied")
        
        member = (
            self.db_session.query(TeamMember)
            .filter(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
            )
            .first()
        )
        
        if not member or member.role != TeamRole.ADMIN:
            raise ValueError("Only team admins can update team settings")
        
        if name is not None:
            team.name = name
        if host_language is not None:
            team.host_language = host_language
        
        team.updated_at = datetime.now(timezone.utc)
        return self.team_repo.update(team)
    
    def get_team_members(self, team_id: uuid.UUID, user_id: uuid.UUID) -> List[dict]:
        """Get team members list."""
        team = self._get_team_with_access(team_id, user_id)
        if not team:
            raise ValueError("Access denied")
        
        members = self.member_repo.list_by_team_id(team_id)
        
        return [
            {
                "id": m.id,
                "user_id": m.user_id,
                "email": m.user.email,
                "full_name": m.user.full_name,
                "role": m.role.value,
                "created_at": m.created_at.isoformat(),
            }
            for m in members
        ]
    
    def get_billing_info(self, team_id: uuid.UUID, user_id: uuid.UUID) -> dict:
        """Get billing information."""
        team = self._get_team_with_access(team_id, user_id)
        if not team:
            raise ValueError("Access denied")
        
        return {
            "plan": team.plan.value,
            "credits_balance": team.credits_balance or 0,
            "stripe_customer_id": team.stripe_customer_id,
            "stripe_subscription_id": team.stripe_subscription_id,
        }
    
    def _get_team_with_access(self, team_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Team]:
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
