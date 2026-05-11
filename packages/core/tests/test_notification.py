"""Tests for NotificationService."""

from unittest.mock import patch

import pytest

from poly_core.services.notification import NotificationService


@pytest.fixture
def mock_templates_dir(tmp_path):
    """Create a temporary templates directory."""
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()

    # Create test templates
    (templates_dir / "verification_email.html").write_text("{{ user_name }} - {{ verification_url }}")
    (templates_dir / "password_reset_email.html").write_text("{{ user_name }} - {{ reset_url }}")
    (templates_dir / "team_invitation_email.html").write_text("{{ invitee_name }} - {{ inviter_name }} - {{ team_name }} - {{ invitation_url }} - {{ role }}")

    return str(templates_dir)


@pytest.fixture
def notification_service(mock_templates_dir):
    """Create a NotificationService instance."""
    return NotificationService(
        smtp_host="smtp.example.com",
        smtp_port=587,
        smtp_user="test@example.com",
        smtp_password="password",
        smtp_from="noreply@example.com",
        templates_dir=mock_templates_dir,
        app_url="https://app.example.com",
    )


class TestNotificationService:
    """Tests for NotificationService."""

    def test_service_initialization(self, notification_service):
        """Verify service initializes correctly."""
        assert notification_service.smtp_host == "smtp.example.com"
        assert notification_service.smtp_port == 587
        assert notification_service.smtp_from == "noreply@example.com"

    def test_send_verification_email(self, notification_service):
        """Verify email verification is sent correctly."""
        with patch.object(notification_service, "_send_email") as mock_send:
            mock_send.return_value = None

            notification_service.send_verification_email(
                user_email="test@example.com",
                user_name="Test User",
                token="verification-token-123",
            )

            mock_send.assert_called_once()
            args = mock_send.call_args[0]
            assert args[0] == "test@example.com"
            assert "Verify your email address" in args[1]

    def test_send_password_reset_email(self, notification_service):
        """Verify password reset email is sent correctly."""
        with patch.object(notification_service, "_send_email") as mock_send:
            mock_send.return_value = None

            notification_service.send_password_reset_email(
                user_email="test@example.com",
                user_name="Test User",
                token="reset-token-123",
            )

            mock_send.assert_called_once()
            args = mock_send.call_args[0]
            assert args[0] == "test@example.com"
            assert "Reset your password" in args[1]

    def test_send_invitation_email(self, notification_service):
        """Verify team invitation email is sent correctly."""
        with patch.object(notification_service, "_send_email") as mock_send:
            mock_send.return_value = None

            notification_service.send_invitation_email(
                invitee_email="invited@example.com",
                inviter_name="Inviter",
                team_name="Test Team",
                token="invite-token-123",
                role="MEMBER",
            )

            mock_send.assert_called_once()
            args = mock_send.call_args[0]
            assert args[0] == "invited@example.com"
            assert "Invitation to join Test Team" in args[1]

    def test_render_template(self, notification_service):
        """Verify template rendering works correctly."""
        html = notification_service._render_template(
            "verification_email.html",
            {"user_name": "John", "verification_url": "https://example.com/verify"},
        )

        assert "John" in html
        assert "https://example.com/verify" in html
