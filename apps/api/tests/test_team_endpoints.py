import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from apps.api.src.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_db():
    db = Mock(spec=Session)
    return db


class TestTeamEndpoints:
    def test_get_team_success(self, client, mock_db):
        with patch("apps.api.src.routes.teams.get_db", return_value=mock_db):
            with patch("apps.api.src.routes.teams.TeamService") as mock_team_service:
                mock_service = Mock()
                mock_team_service.return_value = mock_service

                mock_team = Mock()
                mock_team.id = "team-id"
                mock_team.name = "My Team"
                mock_service.get_team.return_value = mock_team

                response = client.get(
                    "/v1/teams/team-id",
                    headers={"Authorization": "Bearer valid-token"}
                )

                assert response.status_code == 200
                data = response.json()
                assert data["id"] == "team-id"
                assert data["name"] == "My Team"

    def test_get_team_not_found(self, client, mock_db):
        with patch("apps.api.src.routes.teams.get_db", return_value=mock_db):
            with patch("apps.api.src.routes.teams.TeamService") as mock_team_service:
                mock_service = Mock()
                mock_team_service.return_value = mock_service

                mock_service.get_team.side_effect = TeamError("Team not found")

                response = client.get(
                    "/v1/teams/not-found",
                    headers={"Authorization": "Bearer valid-token"}
                )

                assert response.status_code == 404

    def test_create_team_success(self, client, mock_db):
        with patch("apps.api.src.routes.teams.get_db", return_value=mock_db):
            with patch("apps.api.src.routes.teams.TeamService") as mock_team_service:
                mock_service = Mock()
                mock_team_service.return_value = mock_service

                mock_team = Mock()
                mock_team.id = "team-id"
                mock_team.name = "New Team"
                mock_service.create_team.return_value = mock_team

                response = client.post(
                    "/v1/teams",
                    headers={"Authorization": "Bearer valid-token"},
                    json={"name": "New Team", "language": "en"}
                )

                assert response.status_code == 200
                data = response.json()
                assert data["id"] == "team-id"
                assert data["name"] == "New Team"

    def test_update_team_success(self, client, mock_db):
        with patch("apps.api.src.routes.teams.get_db", return_value=mock_db):
            with patch("apps.api.src.routes.teams.TeamService") as mock_team_service:
                mock_service = Mock()
                mock_team_service.return_value = mock_service

                mock_team = Mock()
                mock_team.id = "team-id"
                mock_team.name = "Updated Team"
                mock_service.update_team.return_value = mock_team

                response = client.patch(
                    "/v1/teams/team-id",
                    headers={"Authorization": "Bearer valid-token"},
                    json={"name": "Updated Team"}
                )

                assert response.status_code == 200
                data = response.json()
                assert data["name"] == "Updated Team"

    def test_delete_team_success(self, client, mock_db):
        with patch("apps.api.src.routes.teams.get_db", return_value=mock_db):
            with patch("apps.api.src.routes.teams.TeamService") as mock_team_service:
                mock_service = Mock()
                mock_team_service.return_value = mock_service

                response = client.delete(
                    "/v1/teams/team-id",
                    headers={"Authorization": "Bearer valid-token"}
                )

                assert response.status_code == 204

    def test_get_members_success(self, client, mock_db):
        with patch("apps.api.src.routes.teams.get_db", return_value=mock_db):
            with patch("apps.api.src.routes.teams.TeamService") as mock_team_service:
                mock_service = Mock()
                mock_team_service.return_value = mock_service

                mock_member1 = Mock()
                mock_member1.id = "member1-id"
                mock_member1.role = "ADMIN"

                mock_member2 = Mock()
                mock_member2.id = "member2-id"
                mock_member2.role = "MEMBER"

                mock_service.get_members.return_value = [mock_member1, mock_member2]

                response = client.get(
                    "/v1/teams/team-id/members",
                    headers={"Authorization": "Bearer valid-token"}
                )

                assert response.status_code == 200
                data = response.json()
                assert len(data) == 2

    def test_add_member_success(self, client, mock_db):
        with patch("apps.api.src.routes.teams.get_db", return_value=mock_db):
            with patch("apps.api.src.routes.teams.InvitationService") as mock_inv_service:
                mock_service = Mock()
                mock_inv_service.return_value = mock_service

                mock_invitation = Mock()
                mock_invitation.id = "inv-id"
                mock_invitation.token = "invite-token"
                mock_service.create_invitation.return_value = mock_invitation

                response = client.post(
                    "/v1/teams/team-id/invitations",
                    headers={"Authorization": "Bearer valid-token"},
                    json={
                        "email": "newuser@example.com",
                        "role": "MEMBER"
                    }
                )

                assert response.status_code == 200
                data = response.json()
                assert data["id"] == "inv-id"

    def test_accept_invitation_success(self, client, mock_db):
        with patch("apps.api.src.routes.teams.get_db", return_value=mock_db):
            with patch("apps.api.src.routes.teams.InvitationService") as mock_inv_service:
                mock_service = Mock()
                mock_inv_service.return_value = mock_service

                mock_team_member = Mock()
                mock_team_member.id = "member-id"
                mock_service.accept_invitation.return_value = mock_team_member

                response = client.post(
                    "/v1/invitations/invite-token/accept",
                    headers={"Authorization": "Bearer valid-token"},
                    json={}
                )

                assert response.status_code == 200
                data = response.json()
                assert data["id"] == "member-id"

    def test_update_member_role_success(self, client, mock_db):
        with patch("apps.api.src.routes.teams.get_db", return_value=mock_db):
            with patch("apps.api.src.routes.teams.TeamService") as mock_team_service:
                mock_service = Mock()
                mock_team_service.return_value = mock_service

                mock_member = Mock()
                mock_member.id = "member-id"
                mock_member.role = "ADMIN"
                mock_service.update_member_role.return_value = mock_member

                response = client.patch(
                    "/v1/teams/team-id/members/user-id",
                    headers={"Authorization": "Bearer valid-token"},
                    json={"role": "ADMIN"}
                )

                assert response.status_code == 200
                data = response.json()
                assert data["role"] == "ADMIN"

    def test_remove_member_success(self, client, mock_db):
        with patch("apps.api.src.routes.teams.get_db", return_value=mock_db):
            with patch("apps.api.src.routes.teams.TeamService") as mock_team_service:
                mock_service = Mock()
                mock_team_service.return_value = mock_service

                response = client.delete(
                    "/v1/teams/team-id/members/user-id",
                    headers={"Authorization": "Bearer valid-token"}
                )

                assert response.status_code == 204
