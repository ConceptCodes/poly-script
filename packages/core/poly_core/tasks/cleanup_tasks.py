from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from poly_db.repositories import UserRepository


def cleanup_expired_password_resets(db: Session) -> Dict[str, int]:
    """Delete expired password reset tokens"""
    from poly_db.repositories.auth import PasswordResetRepository

    password_reset_repo = PasswordResetRepository(db)
    expired_tokens = password_reset_repo.delete_expired()

    return {"deleted_password_resets": len(expired_tokens)}


def cleanup_expired_invitations(db: Session) -> Dict[str, int]:
    """Delete expired team invitations"""
    from poly_db.repositories.teams import TeamInvitationRepository

    invitation_repo = TeamInvitationRepository(db)
    expired_invitations = invitation_repo.delete_expired()

    return {"deleted_invitations": len(expired_invitations)}


def cleanup_revoked_tokens(db: Session) -> Dict[str, int]:
    """Delete revoked refresh tokens"""
    from poly_db.repositories.auth import RefreshTokenRepository

    refresh_token_repo = RefreshTokenRepository(db)
    deleted_tokens = refresh_token_repo.delete_revoked()

    return {"deleted_tokens": len(deleted_tokens)}


def cleanup_soft_deleted_users(db: Session, grace_days: int) -> Dict[str, int]:
    """Hard delete users soft-deleted beyond grace period."""
    from datetime import timezone

    user_repo = UserRepository(db)
    cutoff = datetime.now(timezone.utc) - timedelta(days=grace_days)

    users = [u for u in user_repo.list() if u.deleted_at and u.deleted_at < cutoff]
    deleted = 0
    for user in users:
        if user_repo.delete(user.id):
            deleted += 1

    return {"deleted_users": deleted}
