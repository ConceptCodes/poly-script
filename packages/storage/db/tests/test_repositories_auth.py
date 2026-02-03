from datetime import UTC, datetime, timedelta

from poly_db.models import OAuthAccount, PasswordReset, RefreshToken, User
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
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    expired_reset = PasswordReset(
        user_id=user.id,
        token="reset-expired",
        expires_at=datetime.now(UTC) - timedelta(hours=1),
    )
    session.add_all([reset, expired_reset])

    refresh = RefreshToken(
        user_id=user.id,
        token="refresh-token",
        expires_at=datetime.now(UTC) + timedelta(days=7),
        revoked=False,
    )
    revoked_refresh = RefreshToken(
        user_id=user.id,
        token="refresh-revoked",
        expires_at=datetime.now(UTC) + timedelta(days=7),
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


def test_auth_repositories_negative_cases(session):
    user = User(email="auth2@example.com", hashed_password="pw", is_verified=True)
    session.add(user)
    session.commit()

    oauth_repo = OAuthAccountRepository(session)
    assert oauth_repo.get_by_provider("google", "nonexistent") is None
    assert oauth_repo.get_by_user_id(user.id) == []

    reset_repo = PasswordResetRepository(session)
    assert reset_repo.get_by_token("nonexistent") is None
    assert reset_repo.get_active_by_token("nonexistent") is None

    active_reset = PasswordReset(
        user_id=user.id,
        token="active-reset",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
        used_at=datetime.now(UTC),
    )
    session.add(active_reset)
    session.commit()

    assert reset_repo.get_by_token("active-reset").id == active_reset.id
    assert reset_repo.get_active_by_token("active-reset") is None

    refresh_repo = RefreshTokenRepository(session)
    assert refresh_repo.get_by_token("nonexistent") is None
    assert refresh_repo.get_active_by_token("nonexistent") is None
    assert refresh_repo.list_by_user_id(user.id) == []

    assert refresh_repo.delete_revoked() == []


def test_auth_repositories_base_methods(session):
    user = User(email="auth3@example.com", hashed_password="pw", is_verified=True)
    session.add(user)
    session.commit()

    oauth_repo = OAuthAccountRepository(session)
    new_oauth = oauth_repo.create(
        user_id=user.id,
        provider="github",
        provider_user_id="github-123",
    )
    assert new_oauth.id is not None

    updated_oauth = oauth_repo.update(new_oauth.id, provider_user_id="github-456")
    assert updated_oauth.provider_user_id == "github-456"

    assert oauth_repo.delete(new_oauth.id) is True
    assert oauth_repo.get(new_oauth.id) is None

    reset_repo = PasswordResetRepository(session)
    new_reset = reset_repo.create(
        user_id=user.id,
        token="new-reset-token",
        expires_at=datetime.now(UTC) + timedelta(hours=2),
    )
    assert new_reset.id is not None

    updated_reset = reset_repo.update(new_reset.id, used_at=datetime.now(UTC))
    assert updated_reset.used_at is not None

    assert reset_repo.delete(new_reset.id) is True

    refresh_repo = RefreshTokenRepository(session)
    new_refresh = refresh_repo.create(
        user_id=user.id,
        token="new-refresh-token",
        expires_at=datetime.now(UTC) + timedelta(days=14),
        revoked=False,
    )
    assert new_refresh.id is not None

    updated_refresh = refresh_repo.update(new_refresh.id, revoked=True)
    assert updated_refresh.revoked is True

    assert refresh_repo.delete(new_refresh.id) is True
