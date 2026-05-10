import uuid
import sys
from pathlib import Path

# Add apps/api to path before other imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from . import setup_paths as _setup_paths
from ..main import app

del _setup_paths


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_db():
    db = Mock(spec=Session)
    return db


class TestTeamEndpoints:
    def test_get_team_success(self, client, mock_db):
        with patch("src.dependencies.get_db_session", return_value=mock_db):
            with patch("src.routes.teams.get_team_service") as mock_team_service_dep:
                mock_service = Mock()
                mock_team_service_dep.return_value = mock_service

                mock_team = Mock()
                mock_team.id = uuid.uuid4()
                mock_team.name = "My Team"
                mock_service.get_team.return_value = mock_team

                response = client.get(
                    f"/v1/teams/{mock_team.id}",
                    headers={"Authorization": "Bearer valid-token"},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["id"] == str(mock_team.id)
                assert data["name"] == "My Team"

    def test_get_team_not_found(self, client, mock_db):
        with patch("src.dependencies.get_db_session", return_value=mock_db):
            with patch("src.routes.teams.get_team_service") as mock_team_service_dep:
                mock_service = Mock()
                mock_team_service_dep.return_value = mock_service

                mock_service.get_team.return_value = None

                response = client.get(
                    "/v1/teams/not-found-id",
                    headers={"Authorization": "Bearer valid-token"},
                )

                assert response.status_code == 404

    def test_create_team_success(self, client, mock_db):
        with patch("src.dependencies.get_db_session", return_value=mock_db):
            with patch("src.routes.teams.get_team_service") as mock_team_service_dep:
                mock_service = Mock()
                mock_team_service_dep.return_value = mock_service

                mock_team = Mock()
                mock_team.id = uuid.uuid4()
                mock_team.name = "New Team"
                mock_service.create_team.return_value = mock_team

                response = client.post(
                    "/v1/teams",
                    headers={"Authorization": "Bearer valid-token"},
                    json={"name": "New Team", "language": "en"},
                )

                assert response.status_code == 201
                data = response.json()
                assert data["id"] == str(mock_team.id)
                assert data["name"] == "New Team"

    def test_update_team_success(self, client, mock_db):
        with patch("src.dependencies.get_db_session", return_value=mock_db):
            with patch("src.routes.teams.get_team_service") as mock_team_service_dep:
                mock_service = Mock()
                mock_team_service_dep.return_value = mock_service

                mock_team = Mock()
                mock_team.id = uuid.uuid4()
                mock_team.name = "Updated Team"
                mock_service.update_team.return_value = mock_team

                response = client.patch(
                    f"/v1/teams/{mock_team.id}",
                    headers={"Authorization": "Bearer valid-token"},
                    json={"name": "Updated Team"},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["name"] == "Updated Team"

    def test_delete_team_success(self, client, mock_db):
        with patch("src.dependencies.get_db_session", return_value=mock_db):
            with patch("src.routes.teams.get_team_service") as mock_team_service_dep:
                mock_service = Mock()
                mock_team_service_dep.return_value = mock_service

                mock_service.delete_team.return_value = True

                response = client.delete(
                    "/v1/teams/team-id",
                    headers={"Authorization": "Bearer valid-token"},
                )

                assert response.status_code == 204

    def test_get_members_success(self, client, mock_db):
        with patch("src.dependencies.get_db_session", return_value=mock_db):
            with patch("src.routes.teams.get_team_service") as mock_team_service_dep:
                mock_service = Mock()
                mock_team_service_dep.return_value = mock_service

                mock_member1 = Mock()
                mock_member1.id = uuid.uuid4()
                mock_member1.role = "ADMIN"

                mock_member2 = Mock()
                mock_member2.id = uuid.uuid4()
                mock_member2.role = "MEMBER"

                mock_service.get_members.return_value = [mock_member1, mock_member2]

                response = client.get(
                    "/v1/teams/team-id/members",
                    headers={"Authorization": "Bearer valid-token"},
                )

                assert response.status_code == 200
                data = response.json()
                assert len(data) == 2

    def test_send_invitation_success(self, client, mock_db):
        with patch("src.dependencies.get_db_session", return_value=mock_db):
            with patch("src.routes.teams.get_invitation_service") as mock_inv_service_dep:
                mock_service = Mock()
                mock_inv_service_dep.return_value = mock_service

                mock_invitation = Mock()
                mock_invitation.id = uuid.uuid4()
                mock_invitation.token = "invite-token"
                mock_service.create_invitation.return_value = mock_invitation

                response = client.post(
                    "/v1/teams/team-id/invitations",
                    headers={"Authorization": "Bearer valid-token"},
                    json={"email": "newuser@example.com", "role": "MEMBER"},
                )

                assert response.status_code == 201
                data = response.json()
                assert data["id"] == str(mock_invitation.id)

    def test_accept_invitation_success(self, client, mock_db):
        with patch("src.dependencies.get_db_session", return_value=mock_db):
            with patch("src.routes.teams.get_invitation_service") as mock_inv_service_dep:
                mock_service = Mock()
                mock_inv_service_dep.return_value = mock_service

                mock_team_member = Mock()
                mock_team_member.id = uuid.uuid4()
                mock_service.accept_invitation.return_value = mock_team_member

                response = client.post(
                    "/v1/invitations/test-token/accept",
                    headers={"Authorization": "Bearer valid-token"},
                )

                assert response.status_code == 204

    def test_update_member_role_success(self, client, mock_db):
        with patch("src.dependencies.get_db_session", return_value=mock_db):
            with patch("src.routes.teams.get_team_service") as mock_team_service_dep:
                mock_service = Mock()
                mock_team_service_dep.return_value = mock_service

                mock_member = Mock()
                mock_member.id = uuid.uuid4()
                mock_member.role = "ADMIN"
                mock_service.update_member_role.return_value = mock_member

                response = client.patch(
                    "/v1/teams/team-id/members/user-id",
                    headers={"Authorization": "Bearer valid-token"},
                    json={"role": "ADMIN"},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["role"] == "ADMIN"

    def test_remove_member_success(self, client, mock_db):
        with patch("src.dependencies.get_db_session", return_value=mock_db):
            with patch("src.routes.teams.get_team_service") as mock_team_service_dep:
                mock_service = Mock()
                mock_team_service_dep.return_value = mock_service

                mock_service.remove_member.return_value = True

                response = client.delete(
                    "/v1/teams/team-id/members/user-id",
                    headers={"Authorization": "Bearer valid-token"},
                )

                assert response.status_code == 204
