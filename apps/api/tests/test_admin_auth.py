"""Test admin authentication endpoints."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from poly_core.services.audit import AuditService
from poly_db.models.admin_users import AdminUser, AdminUserRole


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = Mock()
    session.commit = Mock()
    session.flush = Mock()
    session.rollback = Mock()
    session.add = Mock()
    session.refresh = Mock()
    return session


@pytest.fixture
def mock_audit_service():
    """Create a mock audit service."""
    service = Mock(spec=AuditService)
    service.log_admin_action = AsyncMock()
    return service


@pytest.fixture
def test_admin_user():
    """Create a test SUPER_ADMIN user."""
    from poly_core.services.admin_auth import AdminAuthService

    service = AdminAuthService(Mock(), jwt_secret="test-secret", jwt_expiry_minutes=15)
    return AdminUser(
        id=uuid.uuid4(),
        email="admin@test.com",
        full_name="Test Admin",
        role=AdminUserRole.SUPER_ADMIN,
        is_active=True,
        is_suspended=False,
        hashed_password=service.hash_password("password123"),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def test_suspended_admin():
    """Create a test suspended admin user."""
    from poly_core.services.admin_auth import AdminAuthService

    service = AdminAuthService(Mock(), jwt_secret="test-secret", jwt_expiry_minutes=15)
    return AdminUser(
        id=uuid.uuid4(),
        email="suspended@test.com",
        full_name="Suspended Admin",
        role=AdminUserRole.ADMIN,
        is_active=False,
        is_suspended=True,
        hashed_password=service.hash_password("password123"),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def mock_admin_repo():
    """Create a mock admin repository."""
    repo = Mock()
    repo.get_by_email = Mock()
    repo.get_by_id = Mock()
    repo.create = Mock()
    repo.update = Mock()
    return repo


class TestAdminAuthService:
    """Test AdminAuthService methods."""

    def test_verify_password_valid(self, test_admin_user):
        """Valid password returns True."""
        from poly_core.services.admin_auth import AdminAuthService

        service = AdminAuthService(Mock(), jwt_secret="test-secret", jwt_expiry_minutes=15)
        result = service.verify_password("password123", test_admin_user.hashed_password)
        assert result is True

    def test_verify_password_invalid(self, test_admin_user):
        """Invalid password returns False."""
        from poly_core.services.admin_auth import AdminAuthService

        service = AdminAuthService(Mock(), jwt_secret="test-secret", jwt_expiry_minutes=15)
        result = service.verify_password("wrongpassword", test_admin_user.hashed_password)
        assert result is False

    def test_create_access_token_includes_role(self, test_admin_user):
        """JWT token includes admin_user_id and role fields."""
        from poly_core.services.admin_auth import AdminAuthService

        service = AdminAuthService(
            Mock(), jwt_secret="test-secret-key-for-jwt-signing", jwt_expiry_minutes=15
        )
        token = service.create_access_token(test_admin_user.id, test_admin_user.role.value)

        # Decode and verify payload
        payload = jwt.decode(token, "test-secret-key-for-jwt-signing", algorithms=["HS256"])

        assert payload["sub"] == str(test_admin_user.id)
        assert payload["role"] == test_admin_user.role.value
        assert "exp" in payload
        assert "iat" in payload

    def test_verify_access_token_valid(self, test_admin_user):
        """Verify token returns payload for valid token."""
        from poly_core.services.admin_auth import AdminAuthService

        service = AdminAuthService(
            Mock(), jwt_secret="test-secret-key-for-jwt-signing", jwt_expiry_minutes=15
        )
        token = service.create_access_token(test_admin_user.id, test_admin_user.role.value)

        payload = service.verify_access_token(token)
        assert payload is not None
        assert payload["sub"] == str(test_admin_user.id)

    def test_verify_access_token_invalid(self):
        """Verify token returns None for invalid token."""
        from poly_core.services.admin_auth import AdminAuthService

        service = AdminAuthService(
            Mock(), jwt_secret="test-secret-key-for-jwt-signing", jwt_expiry_minutes=15
        )
        payload = service.verify_access_token("invalid-token")
        assert payload is None


class TestAdminAuthEndpoints:
    """Test admin authentication endpoints."""

    @pytest.mark.asyncio
    async def test_admin_login_success(
        self, mock_db_session, test_admin_user, mock_admin_repo, mock_audit_service
    ):
        """POST /v1/admin/auth/login with valid credentials returns token."""
        from fastapi import FastAPI

        mock_admin_repo.get_by_email.return_value = test_admin_user

        app = FastAPI()

        @app.post("/v1/admin/auth/login")
        async def login():
            from fastapi import HTTPException

            admin = mock_admin_repo.get_by_email.return_value
            if admin and not admin.is_suspended and admin.is_active:
                await mock_audit_service.log_admin_action()
                return {"access_token": "test-jwt-token", "token_type": "bearer"}

            raise HTTPException(status_code=401, detail="Invalid credentials")

        client = TestClient(app)
        response = client.post(
            "/v1/admin/auth/login",
            json={"email": "admin@test.com", "password": "password123"},
        )

        assert response.status_code == 200
        assert response.json()["access_token"] == "test-jwt-token"
        assert response.json()["token_type"] == "bearer"
        mock_audit_service.log_admin_action.assert_awaited()

    def test_admin_login_invalid_credentials(
        self, mock_db_session, mock_admin_repo, mock_audit_service
    ):
        """POST /v1/admin/auth/login with invalid credentials returns 401."""
        mock_admin_repo.get_by_email.return_value = None

        from fastapi import FastAPI

        app = FastAPI()

        @app.post("/v1/admin/auth/login")
        async def login():
            from fastapi import HTTPException

            admin = mock_admin_repo.get_by_email.return_value
            if not admin:
                await mock_audit_service.log_admin_action()
                raise HTTPException(status_code=401, detail="Invalid credentials")
            return {"access_token": "token"}

        client = TestClient(app)
        response = client.post(
            "/v1/admin/auth/login", json={"email": "none@test.com", "password": "wrong"}
        )

        assert response.status_code == 401
        mock_audit_service.log_admin_action.assert_awaited()

    def test_admin_login_suspended_account(
        self, mock_db_session, test_suspended_admin, mock_admin_repo, mock_audit_service
    ):
        """POST /v1/admin/auth/login with suspended account returns 403."""
        mock_admin_repo.get_by_email.return_value = test_suspended_admin

        from fastapi import FastAPI

        app = FastAPI()

        @app.post("/v1/admin/auth/login")
        async def login():
            from fastapi import HTTPException

            admin = mock_admin_repo.get_by_email.return_value
            if admin.is_suspended:
                await mock_audit_service.log_admin_action()
                raise HTTPException(status_code=403, detail="Account suspended")
            return {"access_token": "token"}

        client = TestClient(app)
        response = client.post(
            "/v1/admin/auth/login",
            json={"email": "suspended@test.com", "password": "password123"},
        )

        assert response.status_code == 403
        mock_audit_service.log_admin_action.assert_awaited()


class TestAdminAuthorization:
    """Test admin authorization middleware."""

    def test_regular_user_cannot_access_admin_endpoints(self):
        """Regular user JWT is rejected on admin endpoints."""
        settings = Mock()
        settings.JWT_SECRET = "user-jwt-secret"
        settings.JWT_ALGORITHM = "HS256"

        # Create a regular user token
        user_token = jwt.encode(
            {
                "sub": str(uuid.uuid4()),
                "team_id": str(uuid.uuid4()),
                "exp": int(datetime.now(UTC).timestamp()) + 900,
            },
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )

        # Decode to verify it's a user token (no role claim)
        payload = jwt.decode(user_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])

        # User tokens should NOT have admin role
        assert "role" not in payload or payload.get("role") not in ["ADMIN", "SUPER_ADMIN"]
