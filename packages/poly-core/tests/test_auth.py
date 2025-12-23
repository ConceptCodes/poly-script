import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from poly_core.services.auth import (
    AuthService,
    AuthError,
    EmailVerificationError,
    PasswordResetError,
)


@pytest.fixture
def mock_db():
    db = Mock(spec=Session)
    return db


@pytest.fixture
def auth_service(mock_db):
    return AuthService(mock_db)


class TestAuthService:
    def test_hash_password(self, auth_service):
        password = "test_password_123"
        hashed = auth_service.hash_password(password)

        assert hashed != password
        assert isinstance(hashed, str)
        assert hashed.startswith("$2b$")

    def test_verify_password_valid(self, auth_service):
        password = "test_password_123"
        hashed = auth_service.hash_password(password)

        result = auth_service.verify_password(password, hashed)
        assert result is True

    def test_verify_password_invalid(self, auth_service):
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = auth_service.hash_password(password)

        result = auth_service.verify_password(wrong_password, hashed)
        assert result is False

    def test_generate_email_verification_token(self, auth_service):
        user_id = "user-uuid"

        token = auth_service._generate_email_verification_token(user_id)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) == 32

    def test_generate_password_reset_token(self, auth_service):
        user_id = "user-uuid"

        token = auth_service._generate_password_reset_token(user_id)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) == 32

    def test_create_access_token(self, auth_service):
        user_id = "user-uuid"

        token = auth_service._create_access_token(user_id)

        assert token is not None
        assert isinstance(token, str)
        parts = token.split(".")
        assert len(parts) == 3

    def test_create_refresh_token(self, auth_service):
        user_id = "user-uuid"

        token = auth_service._create_refresh_token(user_id)

        assert token is not None
        assert isinstance(token, str)
        parts = token.split(".")
        assert len(parts) == 3

    @patch("poly_core.services.auth.NotificationService")
    def test_send_verification_email(self, mock_notification_class, mock_db, auth_service):
        mock_user = Mock()
        mock_user.id = "user-id"
        mock_user.email = "test@example.com"
        mock_user.verification_token = None

        mock_user_repo = Mock()
        mock_user_repo.get_by_email.return_value = mock_user

        mock_db.add = Mock()
        mock_db.commit = Mock()

        with patch.object(auth_service, "user_repo", mock_user_repo):
            auth_service.send_verification_email("test@example.com", "en")

            mock_user_repo.get_by_email.assert_called_once_with("test@example.com")
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()

    @patch("poly_core.services.auth.NotificationService")
    def test_send_verification_email_user_not_found(
        self, mock_notification_class, mock_db, auth_service
    ):
        mock_user_repo = Mock()
        mock_user_repo.get_by_email.return_value = None

        with patch.object(auth_service, "user_repo", mock_user_repo):
            with pytest.raises(AuthError):
                auth_service.send_verification_email("notfound@example.com", "en")

    @patch("poly_core.services.auth.NotificationService")
    def test_verify_email_success(self, mock_notification_class, mock_db, auth_service):
        mock_user = Mock()
        mock_user.verification_token = "valid-token"
        mock_user.is_verified = False

        mock_user_repo = Mock()
        mock_user_repo.get_by_verification_token.return_value = mock_user

        mock_db.add = Mock()
        mock_db.commit = Mock()

        with patch.object(auth_service, "user_repo", mock_user_repo):
            result = auth_service.verify_email("valid-token")

            assert result is not None
            assert mock_user.is_verified is True
            assert mock_user.verification_token is None
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()

    def test_verify_email_invalid_token(self, mock_db, auth_service):
        mock_user_repo = Mock()
        mock_user_repo.get_by_verification_token.return_value = None

        with patch.object(auth_service, "user_repo", mock_user_repo):
            with pytest.raises(EmailVerificationError):
                auth_service.verify_email("invalid-token")

    def test_verify_email_already_verified(self, mock_db, auth_service):
        mock_user = Mock()
        mock_user.verification_token = "valid-token"
        mock_user.is_verified = True

        mock_user_repo = Mock()
        mock_user_repo.get_by_verification_token.return_value = mock_user

        with patch.object(auth_service, "user_repo", mock_user_repo):
            with pytest.raises(EmailVerificationError):
                auth_service.verify_email("valid-token")

    @patch("poly_core.services.auth.NotificationService")
    def test_request_password_reset(self, mock_notification_class, mock_db, auth_service):
        mock_user = Mock()
        mock_user.id = "user-id"
        mock_user.email = "test@example.com"

        mock_user_repo = Mock()
        mock_user_repo.get_by_email.return_value = mock_user

        mock_password_reset_repo = Mock()
        mock_password_reset_repo.delete_by_user.return_value = None
        mock_password_reset_repo.create.return_value = None

        mock_db.add = Mock()
        mock_db.commit = Mock()

        with patch.object(auth_service, "user_repo", mock_user_repo):
            with patch.object(auth_service, "password_reset_repo", mock_password_reset_repo):
                auth_service.request_password_reset("test@example.com", "en")

                mock_user_repo.get_by_email.assert_called_once_with("test@example.com")
                mock_password_reset_repo.delete_by_user.assert_called_once()
                mock_db.add.assert_called()
                mock_db.commit.assert_called()

    def test_reset_password_success(self, mock_db, auth_service):
        mock_password_reset = Mock()
        mock_password_reset.user_id = "user-id"
        mock_password_reset.expires_at = datetime.utcnow() + timedelta(hours=1)
        mock_password_reset.used_at = None

        mock_user = Mock()
        mock_user.id = "user-id"

        mock_password_reset_repo = Mock()
        mock_password_reset_repo.get_by_token.return_value = mock_password_reset

        mock_user_repo = Mock()
        mock_user_repo.get.return_value = mock_user

        mock_db.add = Mock()
        mock_db.commit = Mock()

        with patch.object(auth_service, "password_reset_repo", mock_password_reset_repo):
            with patch.object(auth_service, "user_repo", mock_user_repo):
                auth_service.reset_password("valid-token", "new_password_123")

                assert mock_user.hashed_password is not None
                assert mock_password_reset.used_at is not None
                mock_db.add.assert_called()
                mock_db.commit.assert_called()

    def test_reset_password_token_not_found(self, mock_db, auth_service):
        mock_password_reset_repo = Mock()
        mock_password_reset_repo.get_by_token.return_value = None

        with patch.object(auth_service, "password_reset_repo", mock_password_reset_repo):
            with pytest.raises(PasswordResetError):
                auth_service.reset_password("invalid-token", "new_password")

    def test_reset_password_token_expired(self, mock_db, auth_service):
        mock_password_reset = Mock()
        mock_password_reset.user_id = "user-id"
        mock_password_reset.expires_at = datetime.utcnow() - timedelta(hours=1)
        mock_password_reset.used_at = None

        mock_password_reset_repo = Mock()
        mock_password_reset_repo.get_by_token.return_value = mock_password_reset

        with patch.object(auth_service, "password_reset_repo", mock_password_reset_repo):
            with pytest.raises(PasswordResetError):
                auth_service.reset_password("expired-token", "new_password")

    def test_reset_password_already_used(self, mock_db, auth_service):
        mock_password_reset = Mock()
        mock_password_reset.user_id = "user-id"
        mock_password_reset.expires_at = datetime.utcnow() + timedelta(hours=1)
        mock_password_reset.used_at = datetime.utcnow()

        mock_password_reset_repo = Mock()
        mock_password_reset_repo.get_by_token.return_value = mock_password_reset

        with patch.object(auth_service, "password_reset_repo", mock_password_reset_repo):
            with pytest.raises(PasswordResetError):
                auth_service.reset_password("used-token", "new_password")

    @patch("poly_core.services.auth.NotificationService")
    def test_signup_success(self, mock_notification_class, mock_db, auth_service):
        mock_user = Mock()
        mock_user.id = "user-id"

        mock_user_repo = Mock()
        mock_user_repo.get_by_email.return_value = None
        mock_user_repo.create.return_value = mock_user

        mock_team_repo = Mock()
        mock_team = Mock()
        mock_team.id = "team-id"
        mock_team_repo.create.return_value = mock_team

        mock_team_member_repo = Mock()
        mock_team_member_repo.create.return_value = None

        mock_db.add = Mock()
        mock_db.commit = Mock()

        with patch.object(auth_service, "user_repo", mock_user_repo):
            with patch.object(auth_service, "team_repo", mock_team_repo):
                with patch.object(auth_service, "team_member_repo", mock_team_member_repo):
                    result = auth_service.signup(
                        "test@example.com", "password_123", "John Doe", "en"
                    )

                    assert result is not None
                    assert result.id == "user-id"
                    mock_db.add.assert_called()
                    mock_db.commit.assert_called()

    def test_signup_email_exists(self, mock_db, auth_service):
        mock_user = Mock()

        mock_user_repo = Mock()
        mock_user_repo.get_by_email.return_value = mock_user

        with patch.object(auth_service, "user_repo", mock_user_repo):
            with pytest.raises(AuthError):
                auth_service.signup("exists@example.com", "password_123", "John Doe", "en")
