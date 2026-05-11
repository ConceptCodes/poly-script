import uuid
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from src.dependencies import get_current_user
from src.routes.teams import get_invitation_service, get_team_service

from ..main import app
from . import setup_paths as _setup_paths

del _setup_paths


@pytest.fixture
def client():
    original_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_current_user] = lambda: {
        "id": uuid.UUID("550e8400-e29b-41d4-a716-446655440010"),
        "email": "member@example.com",
    }
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides = original_overrides


@pytest.fixture
def team_service():
    service = Mock()
    app.dependency_overrides[get_team_service] = lambda: service
    return service


@pytest.fixture
def invitation_service():
    service = Mock()
    app.dependency_overrides[get_invitation_service] = lambda: service
    return service


def team_response(**overrides):
    values = {
        "id": uuid.UUID("550e8400-e29b-41d4-a716-446655440000"),
        "name": "My Team",
        "host_language": "en",
        "plan": "FREE",
        "monthly_upload_count": 0,
        "extra_credits": 0,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def member_response(**overrides):
    values = {
        "id": uuid.UUID("550e8400-e29b-41d4-a716-446655440001"),
        "user_id": uuid.UUID("550e8400-e29b-41d4-a716-446655440010"),
        "team_id": uuid.UUID("550e8400-e29b-41d4-a716-446655440000"),
        "role": "MEMBER",
        "created_at": "2026-01-01T00:00:00Z",
        "user_email": "member@example.com",
        "user_full_name": "Member User",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def invitation_response(**overrides):
    values = {
        "id": uuid.UUID("550e8400-e29b-41d4-a716-446655440002"),
        "team_id": uuid.UUID("550e8400-e29b-41d4-a716-446655440000"),
        "email": "newuser@example.com",
        "role": "MEMBER",
        "expires_at": "2026-02-01T00:00:00Z",
        "accepted_at": None,
        "created_at": "2026-01-01T00:00:00Z",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


class TestTeamEndpoints:
    def test_get_team_success(self, client, team_service):
        team = team_response()
        team_service.get_team.return_value = team

        response = client.get(f"/v1/teams/{team.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(team.id)
        assert data["name"] == "My Team"

    def test_get_team_not_found(self, client, team_service):
        team_service.get_team.return_value = None

        response = client.get("/v1/teams/not-found-id")

        assert response.status_code == 404

    def test_create_team_success(self, client, team_service):
        team = team_response(name="New Team")
        team_service.create_team.return_value = team

        response = client.post(
            "/v1/teams",
            json={"name": "New Team", "host_language": "en"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["id"] == str(team.id)
        assert data["name"] == "New Team"

    def test_update_team_success(self, client, team_service):
        team = team_response(name="Updated Team")
        team_service.update_team.return_value = team

        response = client.patch(
            f"/v1/teams/{team.id}",
            json={"name": "Updated Team"},
        )

        assert response.status_code == 200
        assert response.json()["name"] == "Updated Team"

    def test_delete_team_success(self, client, team_service):
        team_service.delete_team.return_value = True

        response = client.delete("/v1/teams/team-id")

        assert response.status_code == 204

    def test_get_members_success(self, client, team_service):
        team_service.get_members.return_value = [
            member_response(role="ADMIN"),
            member_response(id=uuid.UUID("550e8400-e29b-41d4-a716-446655440003")),
        ]

        response = client.get("/v1/teams/team-id/members")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["role"] == "ADMIN"

    def test_send_invitation_success(self, client, invitation_service):
        invitation = invitation_response()
        invitation_service.create_invitation.return_value = invitation

        response = client.post(
            "/v1/teams/team-id/invitations",
            json={"email": "newuser@example.com", "role": "MEMBER"},
        )

        assert response.status_code == 201
        assert response.json()["id"] == str(invitation.id)

    def test_accept_invitation_success(self, client, invitation_service):
        invitation_service.accept_invitation.return_value = True

        response = client.post("/v1/teams/invitations/test-token/accept")

        assert response.status_code == 204

    def test_update_member_role_success(self, client, team_service):
        member = member_response(role="ADMIN")
        team_service.update_member_role.return_value = member

        response = client.patch(
            "/v1/teams/team-id/members/user-id",
            json={"role": "ADMIN"},
        )

        assert response.status_code == 200
        assert response.json()["role"] == "ADMIN"

    def test_remove_member_success(self, client, team_service):
        team_service.remove_member.return_value = True

        response = client.delete("/v1/teams/team-id/members/user-id")

        assert response.status_code == 204
