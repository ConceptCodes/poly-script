"""Test admin user management endpoints."""

import pytest


class TestAdminUsersEndpoints:
    """Test admin user management endpoints."""

    def test_list_users_returns_all_users(self):
        """GET /v1/admin/users returns list of all users."""
        pytest.skip("To be implemented - pagination and filtering")

    def test_list_users_with_search_filters(self):
        """GET /v1/admin/users?q=search filters results."""
        pytest.skip("To be implemented - search by email/name")

    def test_get_user_detail_returns_user(self):
        """GET /v1/admin/users/{user_id} returns user details."""
        pytest.skip("To be implemented")

    def test_get_user_detail_not_found(self):
        """GET /v1/admin/users/{user_id} returns 404 for non-existent user."""
        pytest.skip("To be implemented")

    def test_suspend_user_creates_audit_log(self):
        """POST /v1/admin/users/{user_id}/suspend creates audit log."""
        pytest.skip("To be implemented - audit logging verified")

    def test_unsuspend_user_creates_audit_log(self):
        """POST /v1/admin/users/{user_id}/unsuspend creates audit log."""
        pytest.skip("To be implemented - audit logging verified")

    def test_delete_user_soft_delete(self):
        """DELETE /v1/admin/users/{user_id} performs soft delete."""
        pytest.skip("To be implemented - sets deleted_at")

    def test_impersonate_user_creates_token(self):
        """POST /v1/admin/users/{user_id}/impersonate creates impersonation token."""
        pytest.skip("To be implemented in Task 8")
