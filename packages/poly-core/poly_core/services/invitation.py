from typing import Optional
import uuid
import secrets
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from poly_db.repositories.teams import TeamRepository, TeamMemberRepository, TeamInvitationRepository
from poly_db.models.teams import Team
from poly_db.models.team_members import TeamMember
from poly_db.models.team_invitations import TeamInvitation
from poly_db.models.users import User

from ..constants import TeamRole
from ..types import TeamMemberLimits


class InvitationService:
    def __init__(self, db_session: Session, notification_service):
        self.db_session = db_session
        self.team_repo = TeamRepository(db_session)
        self.member_repo = TeamMemberRepository(db_session)
        self.invitation_repo = TeamInvitationRepository(db_session)
        self.notification_service = notification_service

    def create_invitation(
        self,
        team_id: uuid.UUID,
        inviting_user_id: uuid.UUID,
        email: str,
        role: TeamRole,
        expires_in_hours: int = 7 * 24,
    ) -> Optional[TeamInvitation]:
        team = self.db_session.query(Team).filter(
            Team.id == team_id, Team.deleted_at.is_(None)
        ).first()
        if not team:
            return None

        inviting_member = self.db_session.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == inviting_user_id,
        ).first()
        if not inviting_member or inviting_member.role != TeamRole.ADMIN:
            return None

        existing = self.db_session.query(TeamInvitation).filter(
            TeamInvitation.team_id == team_id,
            TeamInvitation.email == email,
            TeamInvitation.accepted_at.is_(None),
        ).first()
        if existing:
            return None

        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)

        invitation = TeamInvitation(
            team_id=team_id,
            email=email,
            role=role,
            token=token,
            expires_at=expires_at,
            accepted_at=None,
        )
        self.invitation_repo.create(invitation)

        inviter = (
            self.db_session.query(User).filter(User.id == inviting_user_id).first()
        )
        if inviter:
            self.notification_service.send_invitation_email(
                invitee_email=email,
                inviter_name=inviter.full_name,
                team_name=team.name,
                token=token,
                role=role.value,
            )

        return invitation

    def get_pending_invitations(
        self, team_id: uuid.UUID, user_id: uuid.UUID
    ) -> list[TeamInvitation]:
        member = self.db_session.query(TeamMember).filter(
            TeamMember.team_id == team_id, TeamMember.user_id == user_id
        ).first()
        if not member or member.role != TeamRole.ADMIN:
            return []

        return self.invitation_repo.list_by_team_id(team_id)

    def cancel_invitation(
        self, invitation_id: uuid.UUID, user_id: uuid.UUID
    ) -> bool:
        invitation = self.invitation_repo.get_by_id(invitation_id)
        if not invitation:
            return False

        member = self.db_session.query(TeamMember).filter(
            TeamMember.team_id == invitation.team_id,
            TeamMember.user_id == user_id,
        ).first()
        if not member or member.role != TeamRole.ADMIN:
            return False

        self.invitation_repo.delete(invitation_id)
        return True

    def accept_invitation(
        self, token: str, user_id: uuid.UUID
    ) -> Optional[TeamMember]:
        invitation = self.invitation_repo.get_by_token(token)
        if not invitation:
            return None

        if invitation.expires_at < datetime.now(timezone.utc):
            return None

        if invitation.accepted_at is not None:
            return None

        team = (
            self.db_session.query(Team)
            .filter(Team.id == invitation.team_id, Team.deleted_at.is_(None))
            .first()
        )
        if not team:
            return None

        user = self.db_session.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        existing_member = self.db_session.query(TeamMember).filter(
            TeamMember.team_id == invitation.team_id,
            TeamMember.user_id == user_id,
        ).first()
        if existing_member:
            return None

        team_member = TeamMember(
            team_id=invitation.team_id,
            user_id=user_id,
            role=invitation.role,
        )
        self.member_repo.create(team_member)

        invitation.accepted_at = datetime.now(timezone.utc)
        self.db_session.commit()

        return team_member
