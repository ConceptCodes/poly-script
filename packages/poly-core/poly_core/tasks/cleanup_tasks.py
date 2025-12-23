from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Dict, Any


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
