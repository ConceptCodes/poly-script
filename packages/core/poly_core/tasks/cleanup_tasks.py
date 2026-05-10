"""Cron job cleanup tasks for maintenance and data retention policies."""

import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

from sqlalchemy.orm import Session

from poly_core.tasks.billing_tasks import reset_all_monthly_usage, sync_active_subscriptions
from poly_db.database import get_session_factory
from poly_db.repositories import (
    AudioAssetRepository,
    RefreshTokenRepository,
    TeamInvitationRepository,
    TranscriptEditRepository,
    UserRepository,
)
from poly_db.repositories.auth import PasswordResetRepository


def _cleanup_expired_password_resets_internal(db: Session) -> dict[str, int]:
    """Delete expired password reset tokens - internal function requiring db"""
    password_reset_repo = PasswordResetRepository(db)
    expired_tokens = password_reset_repo.delete_expired()
    return {"deleted_password_resets": len(expired_tokens)}


def _cleanup_expired_invitations_internal(db: Session) -> dict[str, int]:
    """Delete expired team invitations - internal function requiring db"""
    invitation_repo = TeamInvitationRepository(db)
    expired_invitations = invitation_repo.delete_expired()
    return {"deleted_invitations": len(expired_invitations)}


def _cleanup_revoked_tokens_internal(db: Session) -> dict[str, int]:
    """Delete revoked refresh tokens older than 7 days - internal function requiring db"""
    refresh_token_repo = RefreshTokenRepository(db)
    deleted_tokens = refresh_token_repo.delete_revoked()
    return {"deleted_tokens": len(deleted_tokens)}


def _cleanup_soft_deleted_users_internal(db: Session, grace_days: int = 30) -> dict[str, int]:
    """Hard delete users soft-deleted beyond grace period - internal function requiring db"""
    user_repo = UserRepository(db)
    cutoff = datetime.now(UTC) - timedelta(days=grace_days)

    users = [u for u in user_repo.list() if u.deleted_at and u.deleted_at < cutoff]
    deleted = 0
    for user in users:
        if user_repo.delete(user.id):
            deleted += 1

    return {"deleted_users": deleted}


def _cleanup_orphaned_content_internal(db: Session, retention_days: int = 90) -> dict[str, int]:
    """Delete orphaned content - internal function requiring db"""
    edit_repo = TranscriptEditRepository(db)
    cutoff = datetime.now(UTC) - timedelta(days=retention_days)

    # Find and delete orphaned edits
    orphaned = edit_repo.list_orphaned(cutoff)
    deleted = 0
    for edit in orphaned:
        if edit_repo.delete(edit.id):
            deleted += 1

    return {"deleted_orphaned_edits": deleted}


def _cleanup_audio_files_internal(db: Session, retention_days: int = 30) -> dict[str, int]:
    """Delete audio files for hard-deleted jobs - internal function requiring db"""
    audio_repo = AudioAssetRepository(db)

    cutoff = datetime.now(UTC) - timedelta(days=retention_days)

    # Find audio assets for deleted jobs
    deleted_files = 0
    storage_backend = os.getenv("STORAGE_BACKEND", "local")
    storage_path = os.getenv("STORAGE_PATH", "./data/audio")

    for asset in audio_repo.list_orphaned(cutoff):
        # Delete file
        if storage_backend == "local":
            file_path = Path(storage_path) / f"{asset.id}.audio"
            if file_path.exists():
                file_path.unlink()
                deleted_files += 1

        # Delete DB record
        audio_repo.delete(asset.id)

    return {"deleted_audio_files": deleted_files}


def _hard_delete_soft_deleted_content_internal(db: Session, grace_days: int = 30) -> dict[str, int]:
    """Find and hard delete records where deleted_at < (now - grace_period) - internal function requiring db"""
    # This is a comprehensive cleanup that handles:
    # - Soft-deleted users
    # - Soft-deleted teams
    # - Soft-deleted jobs
    # - Soft-deleted transcripts

    results = {
        "users": _cleanup_soft_deleted_users_internal(db, grace_days).get("deleted_users", 0),
    }

    return results


# Public wrapper functions for APScheduler (create their own DB sessions)
def cleanup_expired_password_resets() -> dict[str, int]:
    """Delete expired password reset tokens"""
    factory = get_session_factory()
    with factory() as db:
        return _cleanup_expired_password_resets_internal(db)


def cleanup_expired_invitations() -> dict[str, int]:
    """Delete expired team invitations"""
    factory = get_session_factory()
    with factory() as db:
        return _cleanup_expired_invitations_internal(db)


def cleanup_revoked_tokens() -> dict[str, int]:
    """Delete revoked refresh tokens older than 7 days"""
    factory = get_session_factory()
    with factory() as db:
        return _cleanup_revoked_tokens_internal(db)


def cleanup_orphaned_content() -> dict[str, int]:
    """Delete orphaned content (transcript_edits where user is deleted)"""
    factory = get_session_factory()
    with factory() as db:
        return _cleanup_orphaned_content_internal(db)


def cleanup_audio_files() -> dict[str, int]:
    """Delete audio files for hard-deleted jobs"""
    factory = get_session_factory()
    with factory() as db:
        return _cleanup_audio_files_internal(db)


def hard_delete_soft_deleted_content() -> dict[str, int]:
    """Find and hard delete records where deleted_at < (now - grace_period)"""
    factory = get_session_factory()
    with factory() as db:
        return _hard_delete_soft_deleted_content_internal(db)


def run_all_cleanup_tasks() -> dict[str, dict]:
    """Run all cleanup tasks and return results."""
    factory = get_session_factory()
    with factory() as db:
        results = {
            "password_resets": _cleanup_expired_password_resets_internal(db),
            "invitations": _cleanup_expired_invitations_internal(db),
            "revoked_tokens": _cleanup_revoked_tokens_internal(db),
            "monthly_usage": reset_all_monthly_usage(),
            "stripe_sync": sync_active_subscriptions(),
        }
        db.commit()
        return results


def cleanup_soft_deleted_users(db: Session, grace_days: int = 30) -> dict[str, int]:
    """Public wrapper for internal cleanup function"""
    return _cleanup_soft_deleted_users_internal(db, grace_days)


if __name__ == "__main__":
    print("Running cleanup tasks...")  # noqa: T201
    results = run_all_cleanup_tasks()
    for task, result in results.items():
        print(f"{task}: {result}")  # noqa: T201
    print("Cleanup complete.")  # noqa: T201
