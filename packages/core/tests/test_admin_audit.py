# ruff: noqa: ARG001

import uuid
from unittest.mock import Mock

import pytest

from poly_core.services.admin_auth import AdminAuthService
from poly_db.models.admin_users import AdminUser


@pytest.fixture
def db_session():
    session = Mock()
    session.commit = Mock()
    session.flush = Mock()
    session.rollback = Mock()
    return session


@pytest.fixture
def mock_admin_user():
    return AdminUser(
        id=uuid.uuid4(),
        email="admin@example.com",
        full_name="Admin User",
        role="SUPER_ADMIN",
        is_active=True,
        is_suspended=False,
    )


@pytest.fixture
def admin_auth_service(db_session):
    return AdminAuthService(
        db_session=db_session,
        jwt_secret="test-secret",
        jwt_expiry_minutes=60,
    )


# Audit Event Catalog
# ADMIN_AUTH_EVENTS: login_success, login_failure
# ADMIN_USER_EVENTS: create_admin, suspend_admin, unsuspend_admin, delete_admin, change_admin_role, reset_admin_password
# USER_MANAGEMENT_EVENTS: suspend_user, unsuspend_user, delete_user
# TEAM_MANAGEMENT_EVENTS: suspend_team, unsuspend_team, delete_team
# JOB_MANAGEMENT_EVENTS: cancel_job, retry_job


class TestAdminAuthAuditLogging:
    """Test audit logging for admin authentication events."""

    def test_login_success_creates_audit_log(self, db_session, admin_auth_service, mock_admin_user):
        """Login success must create audit log."""
        pytest.skip("Audit logging to be implemented in Task 3 - GREEN phase")

    def test_login_failure_creates_audit_log(self, db_session, admin_auth_service):
        """Login failure (invalid credentials) must create audit log."""
        pytest.skip("Audit logging to be implemented in Task 3 - GREEN phase")

    def test_login_inactive_account_creates_audit_log(self, db_session, admin_auth_service):
        """Login attempt to inactive account must create audit log."""
        pytest.skip("Audit logging to be implemented in Task 3 - GREEN phase")

    def test_login_suspended_account_creates_audit_log(self, db_session, admin_auth_service):
        """Login attempt to suspended account must create audit log."""
        pytest.skip("Audit logging to be implemented in Task 3 - GREEN phase")


class TestAdminUserManagementAuditLogging:
    """Test audit logging for admin user management actions."""

    def test_create_admin_creates_audit_log(self, db_session):
        """Creating a new admin user must create audit log."""
        pytest.skip("Method to be implemented in Task 4 - GREEN phase")

    def test_suspend_admin_creates_audit_log(self, db_session):
        """Suspending an admin user must create audit log."""
        pytest.skip("Method to be implemented in Task 4 - GREEN phase")

    def test_unsuspend_admin_creates_audit_log(self, db_session):
        """Unsuspending an admin user must create audit log."""
        pytest.skip("Method to be implemented in Task 4 - GREEN phase")

    def test_change_admin_role_creates_audit_log(self, db_session):
        """Changing admin role must create audit log."""
        pytest.skip("Method to be implemented in Task 4 - GREEN phase")

    def test_delete_admin_creates_audit_log(self, db_session):
        """Deleting an admin user must create audit log."""
        pytest.skip("Method to be implemented in Task 4 - GREEN phase")


class TestUserManagementAuditLogging:
    """Test audit logging for regular user management by admins."""

    def test_suspend_user_creates_audit_log(self, db_session):
        """Suspending a regular user must create audit log."""
        pytest.skip("Covered by route-level tests in apps/api/tests")

    def test_unsuspend_user_creates_audit_log(self, db_session):
        """Unsuspending a regular user must create audit log."""
        pytest.skip("Covered by route-level tests in apps/api/tests")

    def test_delete_user_creates_audit_log(self, db_session):
        """Deleting a regular user must create audit log."""
        pytest.skip("Covered by route-level tests in apps/api/tests")


class TestTeamManagementAuditLogging:
    """Test audit logging for team management by admins."""

    def test_suspend_team_creates_audit_log(self, db_session):
        """Suspending a team must create audit log."""
        pytest.skip("Method to be implemented in Task 4 - GREEN phase")

    def test_unsuspend_team_creates_audit_log(self, db_session):
        """Unsuspending a team must create audit log."""
        pytest.skip("Method to be implemented in Task 4 - GREEN phase")

    def test_delete_team_creates_audit_log(self, db_session):
        """Deleting a team must create audit log."""
        pytest.skip("Method to be implemented in Task 4 - GREEN phase")


class TestJobManagementAuditLogging:
    """Test audit logging for job management by admins."""

    def test_cancel_job_creates_audit_log(self, db_session):
        """Canceling a job must create audit log."""
        expected_log = {
            "target_type": "job",
            "action": "cancel_job",
        }
        assert "target_type" in expected_log

    def test_retry_job_creates_audit_log(self, db_session):
        """Retrying a job must create audit log."""
        expected_log = {
            "target_type": "job",
            "action": "retry_job",
        }
        assert "target_type" in expected_log
