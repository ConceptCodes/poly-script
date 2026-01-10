from datetime import datetime, timedelta, timezone
from poly_db.models import User, OAuthAccount, PasswordReset, RefreshToken
from poly_db.repositories import (
    OAuthAccountRepository,
    PasswordResetRepository,
    RefreshTokenRepository,
)


def test_auth_repositories(session):
    user = User(email="auth@example.com", hashed_password="pw", is_verified=True)
    session.add(user)
    session.commit()

    oauth = OAuthAccount(user_id=user.id, provider="google", provider_user_id="google-123")
    session.add(oauth)

    reset = PasswordReset(
        user_id=user.id,
        token="reset-token",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    expired_reset = PasswordReset(
        user_id=user.id,
        token="reset-expired",
        expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
    )
    session.add_all([reset, expired_reset])

    refresh = RefreshToken(
        user_id=user.id,
        token="refresh-token",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        revoked=False,
    )
    revoked_refresh = RefreshToken(
        user_id=user.id,
        token="refresh-revoked",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        revoked=True,
    )
    session.add_all([refresh, revoked_refresh])
    session.commit()

    oauth_repo = OAuthAccountRepository(session)
    assert oauth_repo.get_by_provider("google", "google-123").id == oauth.id
    assert oauth_repo.get_by_user_id(user.id)[0].id == oauth.id

    reset_repo = PasswordResetRepository(session)
    assert reset_repo.get_by_token("reset-token").id == reset.id
    assert reset_repo.get_active_by_token("reset-token").id == reset.id
    deleted_resets = reset_repo.delete_expired()
    assert expired_reset.id in [r.id for r in deleted_resets]

    refresh_repo = RefreshTokenRepository(session)
    assert refresh_repo.get_by_token("refresh-token").id == refresh.id
    assert refresh_repo.get_active_by_token("refresh-token").id == refresh.id
    assert refresh_repo.list_by_user_id(user.id)[0].id == refresh.id
    deleted_tokens = refresh_repo.delete_revoked()
    assert revoked_refresh.id in [t.id for t in deleted_tokens]
