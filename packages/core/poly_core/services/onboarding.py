from typing import Optional, List
from datetime import datetime, timezone
import uuid
from sqlalchemy.orm import Session

from poly_db.repositories.users import UserRepository
from poly_db.repositories.teams import TeamRepository, TeamMemberRepository, TeamInvitationRepository
from poly_db.models.users import User
from poly_db.models.teams import Team
from poly_db.models.team_members import TeamMember
from poly_db.models.team_invitations import TeamInvitation

from ..constants import TeamRole, PlanType


class OnboardingService:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.user_repo = UserRepository(db_session)
        self.team_repo = TeamRepository(db_session)
        self.member_repo = TeamMemberRepository(db_session)
        self.invitation_repo = TeamInvitationRepository(db_session)
    
    def complete_onboarding(
        self,
        user_id: uuid.UUID,
        team_name: str,
        host_language: str,
        plan: PlanType = PlanType.FREE,
        invite_emails: Optional[List[str]] = None,
    ) -> Team:
        """Complete onboarding with team creation and plan selection."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Create team
        team = Team(
            name=team_name,
            host_language=host_language,
            plan=plan,
        )
        self.team_repo.create(team)
        
        # Add user as admin
        team_member = TeamMember(
            team_id=team.id,
            user_id=user_id,
            role=TeamRole.ADMIN,
        )
        self.member_repo.create(team_member)
        
        # Send invitations if provided
        if invite_emails:
            for email in invite_emails:
                self._create_invitation(team.id, user_id, email)
        
        return team
    
    def update_onboarding_step(
        self,
        user_id: uuid.UUID,
        step: str,
        data: dict,
    ) -> dict:
        """Update onboarding progress (for multi-step wizard)."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # For now, just return the step data
        # In a real implementation, you might store onboarding progress in a separate table
        return {"step": step, "data": data}
    
    def _create_invitation(
        self,
        team_id: uuid.UUID,
        inviter_id: uuid.UUID,
        email: str,
        role: TeamRole = TeamRole.MEMBER,
    ) -> TeamInvitation:
        """Create an invitation for a new team member."""
        invitation = TeamInvitation(
            team_id=team_id,
            inviter_id=inviter_id,
            email=email,
            role=role,
        )
        return self.invitation_repo.create(invitation)
