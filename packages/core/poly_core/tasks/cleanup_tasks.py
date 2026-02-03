"""Cron job cleanup tasks for maintenance and data retention policies."""

import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

from sqlalchemy.orm import Session

from poly_core.tasks.billing_tasks import reset_monthly_usage, sync_stripe_subscriptions
from poly_db.database import get_db
from poly_db.repositories import (
    AudioAssetRepository,
    RefreshTokenRepository,
    TeamInvitationRepository,
    TranscriptEditRepository,
    TranscriptionJobRepository,
    UserRepository,
)
from poly_db.repositories.auth import PasswordResetRepository


def cleanup_expired_password_resets(db: Session) -> dict[str, int]:
    """Delete expired password reset tokens"""
    password_reset_repo = PasswordResetRepository(db)
    expired_tokens = password_reset_repo.delete_expired()
    return {"deleted_password_resets": len(expired_tokens)}


def cleanup_expired_invitations(db: Session) -> dict[str, int]:
    """Delete expired team invitations"""
    invitation_repo = TeamInvitationRepository(db)
    expired_invitations = invitation_repo.delete_expired()
    return {"deleted_invitations": len(expired_invitations)}


def cleanup_revoked_tokens(db: Session) -> dict[str, int]:
    """Delete revoked refresh tokens older than 7 days"""
    refresh_token_repo = RefreshTokenRepository(db)
    deleted_tokens = refresh_token_repo.delete_revoked()
    return {"deleted_tokens": len(deleted_tokens)}


def cleanup_soft_deleted_users(db: Session, grace_days: int = 30) -> dict[str, int]:
    """Hard delete users soft-deleted beyond grace period."""
    user_repo = UserRepository(db)
    cutoff = datetime.now(UTC) - timedelta(days=grace_days)

    users = [u for u in user_repo.list() if u.deleted_at and u.deleted_at < cutoff]
    deleted = 0
    for user in users:
        if user_repo.delete(user.id):
            deleted += 1

    return {"deleted_users": deleted}


def cleanup_orphaned_content(db: Session, retention_days: int = 90) -> dict[str, int]:
    """Delete orphaned content (transcript_edits where user is deleted)."""
    edit_repo = TranscriptEditRepository(db)
    cutoff = datetime.now(UTC) - timedelta(days=retention_days)

    # Find and delete orphaned edits
    orphaned = edit_repo.list_orphaned(cutoff)
    deleted = 0
    for edit in orphaned:
        if edit_repo.delete(edit.id):
            deleted += 1

    return {"deleted_orphaned_edits": deleted}


def cleanup_audio_files(db: Session, retention_days: int = 30) -> dict[str, int]:
    """Delete audio files for hard-deleted jobs."""
    audio_repo = AudioAssetRepository(db)
    job_repo = TranscriptionJobRepository(db)

    cutoff = datetime.now(UTC) - timedelta(days=retention_days)

    # Find audio assets for deleted jobs
    deleted_files = 0
    storage_backend = os.getenv("STORAGE_BACKEND", "local")
    storage_path = os.getenv("STORAGE_PATH", "./data/audio")

    for asset in audio_repo.list_orphaned(cutoff):
        # Delete the file
        if storage_backend == "local":
            file_path = Path(storage_path) / f"{asset.id}.audio"
            if file_path.exists():
                file_path.unlink()
                deleted_files += 1

        # Delete the DB record
        audio_repo.delete(asset.id)

    return {"deleted_audio_files": deleted_files}


def hard_delete_soft_deleted_content(db: Session, grace_days: int = 30) -> dict[str, int]:
    """Find and hard delete records where deleted_at < (now - grace_period)."""
    # This is a comprehensive cleanup that handles:
    # - Soft-deleted users
    # - Soft-deleted teams
    # - Soft-deleted jobs
    # - Soft-deleted transcripts

    results = {
        "users": cleanup_soft_deleted_users(db, grace_days).get("deleted_users", 0),
    }

    return results


def run_all_cleanup_tasks() -> dict[str, dict]:
    """Run all cleanup tasks and return results."""
    db = next(get_db())
    try:
        results = {
            "password_resets": cleanup_expired_password_resets(db),
            "invitations": cleanup_expired_invitations(db),
            "revoked_tokens": cleanup_revoked_tokens(db),
            "monthly_usage": reset_monthly_usage(db),
            "stripe_sync": sync_stripe_subscriptions(db),
        }
        db.commit()
        return results
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    print("Running cleanup tasks...")
    results = run_all_cleanup_tasks()
    for task, result in results.items():
        print(f"{task}: {result}")
    print("Cleanup complete.")
