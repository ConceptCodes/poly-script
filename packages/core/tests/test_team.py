import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from poly_core.services.team import TeamService, TeamError
from poly_core.constants import TeamRole


@pytest.fixture
def mock_db():
    db = Mock(spec=Session)
    return db


@pytest.fixture
def team_service(mock_db):
    return TeamService(mock_db)


class TestTeamService:
    def test_create_team_success(self, mock_db, team_service):
        mock_user = Mock()
        mock_user.id = "user-id"

        mock_team = Mock()
        mock_team.id = "team-id"

        mock_team_repo = Mock()
        mock_team_repo.create.return_value = mock_team

        mock_team_member = Mock()

        mock_team_member_repo = Mock()
        mock_team_member_repo.create.return_value = mock_team_member
        mock_team_member_repo.get_by_user_and_team.return_value = None

        mock_db.add = Mock()
        mock_db.commit = Mock()

        with patch.object(team_service, "team_repo", mock_team_repo):
            with patch.object(team_service, "team_member_repo", mock_team_member_repo):
                result = team_service.create_team(mock_user.id, "My Team", "en")

                assert result is not None
                assert result.id == "team-id"
                mock_db.add.assert_called()
                mock_db.commit.assert_called()

    def test_create_team_too_many_teams(self, mock_db, team_service):
        mock_user = Mock()
        mock_user.id = "user-id"

        mock_team_repo = Mock()
        mock_team_repo.get_by_user_id.return_value = [Mock(), Mock(), Mock()]

        with patch.object(team_service, "team_repo", mock_team_repo):
            with pytest.raises(TeamError):
                team_service.create_team(mock_user.id, "My Team", "en")

    def test_get_team_success(self, team_service):
        mock_team = Mock()
        mock_team.id = "team-id"

        mock_team_repo = Mock()
        mock_team_repo.get.return_value = mock_team

        with patch.object(team_service, "team_repo", mock_team_repo):
            result = team_service.get_team("team-id", "user-id")

            assert result is not None
            assert result.id == "team-id"

    def test_get_team_not_found(self, team_service):
        mock_team_repo = Mock()
        mock_team_repo.get.return_value = None

        with patch.object(team_service, "team_repo", mock_team_repo):
            with pytest.raises(TeamError):
                team_service.get_team("not-found", "user-id")

    def test_get_team_not_member(self, team_service):
        mock_team = Mock()
        mock_team.id = "team-id"

        mock_team_repo = Mock()
        mock_team_repo.get.return_value = mock_team

        mock_team_member_repo = Mock()
        mock_team_member_repo.get.return_value = None
        mock_team_member_repo.get_by_user_and_team.return_value = None

        with patch.object(team_service, "team_repo", mock_team_repo):
            with patch.object(team_service, "team_member_repo", mock_team_member_repo):
                with pytest.raises(TeamError):
                    team_service.get_team("team-id", "other-user-id")

    def test_update_team_success(self, mock_db, team_service):
        mock_team = Mock()
        mock_team.id = "team-id"
        mock_team.name = "Old Name"

        mock_team_repo = Mock()
        mock_team_repo.get.return_value = mock_team

        target_member = Mock()
        requesting_member = Mock()
        requesting_member.role = TeamRole.ADMIN

        mock_team_member_repo = Mock()
        mock_team_member_repo.get_by_user_and_team.return_value = None
        def get_side_effect(user_id):
            return requesting_member if user_id == "admin-id" else target_member
        mock_team_member_repo.get.side_effect = get_side_effect
        mock_team_member_repo.list_by_team_id.return_value = []
        mock_team_member_repo.get_by_user_and_team.return_value = Mock()
        mock_team_member_repo.get_by_user_and_team.return_value = Mock()
        mock_team_member_repo.get_by_user_and_team.return_value = Mock()

        mock_db.commit = Mock()

        with patch.object(team_service, "team_repo", mock_team_repo):
            with patch.object(team_service, "team_member_repo", mock_team_member_repo):
                result = team_service.update_team("team-id", "user-id", "New Name", None)

                assert result.name == "New Name"
                mock_db.commit.assert_called_once()

    def test_delete_team_success(self, mock_db, team_service):
        mock_team = Mock()
        mock_team.id = "team-id"

        mock_team_repo = Mock()
        mock_team_repo.get.return_value = mock_team

        mock_team_member_repo = Mock()
        mock_team_member_repo.get.return_value = Mock()

        mock_db.commit = Mock()

        with patch.object(team_service, "team_repo", mock_team_repo):
            with patch.object(team_service, "team_member_repo", mock_team_member_repo):
                team_service.delete_team("team-id", "user-id")

                assert mock_team.deleted_at is not None
                mock_db.commit.assert_called_once()

    def test_add_member_success(self, mock_db, team_service):
        mock_team = Mock()
        mock_team.id = "team-id"
        mock_team.plan = "FREE"

        mock_new_user = Mock()
        mock_new_user.id = "new-user-id"

        mock_team_member = Mock()

        mock_team_repo = Mock()
        mock_team_repo.get.return_value = mock_team

        mock_user_repo = Mock()
        mock_user_repo.get.return_value = mock_new_user

        mock_team_member_repo = Mock()
        mock_team_member_repo.get.return_value = None
        mock_team_member_repo.create.return_value = mock_team_member
        mock_team_member_repo.get_by_user_and_team.return_value = None
        mock_team_member_repo.list_by_team_id.return_value = []

        mock_db.add = Mock()
        mock_db.commit = Mock()

        with patch.object(team_service, "team_repo", mock_team_repo):
            with patch.object(team_service, "user_repo", mock_user_repo):
                with patch.object(team_service, "team_member_repo", mock_team_member_repo):
                    result = team_service.add_member("team-id", "admin-id", "new-user-id", "MEMBER")

                    assert result is not None
                    mock_db.add.assert_called()
                    mock_db.commit.assert_called()

    def test_add_member_not_admin(self, team_service):
        mock_team = Mock()
        mock_team.id = "team-id"

        mock_team_repo = Mock()
        mock_team_repo.get.return_value = mock_team

        mock_team_member_repo = Mock()
        mock_team_member_repo.get.return_value = Mock()

        with patch.object(team_service, "team_repo", mock_team_repo):
            with patch.object(team_service, "team_member_repo", mock_team_member_repo):
                with pytest.raises(TeamError):
                    team_service.add_member("team-id", "member-id", "new-user-id", "MEMBER")

    def test_remove_member_success(self, mock_db, team_service):
        mock_team = Mock()
        mock_team.id = "team-id"

        target_member = Mock()
        requesting_member = Mock()
        requesting_member.role = TeamRole.ADMIN

        mock_team_member_repo = Mock()
        mock_team_member_repo.get_by_user_and_team.return_value = None
        def get_side_effect(user_id):
            return requesting_member if user_id == "admin-id" else target_member
        mock_team_member_repo.get.side_effect = get_side_effect
        mock_team_member_repo.list_by_team_id.return_value = []

        mock_db.delete = Mock()
        mock_db.commit = Mock()

        mock_team_repo = Mock()
        mock_team_repo.get.return_value = mock_team

        with patch.object(team_service, "team_repo", mock_team_repo):
            with patch.object(team_service, "team_member_repo", mock_team_member_repo):
                team_service.remove_member("team-id", "admin-id", "user-id")

                mock_db.delete.assert_called()
                mock_db.commit.assert_called_once()

    def test_update_member_role_success(self, mock_db, team_service):
        mock_team = Mock()
        mock_team.id = "team-id"

        mock_team_member = Mock()
        mock_team_member.role = "MEMBER"

        mock_team_repo = Mock()
        mock_team_repo.get.return_value = mock_team

        mock_team_member_repo = Mock()
        mock_team_member_repo.get.return_value = mock_team_member
        mock_team_member_repo.get_by_user_and_team.return_value = mock_team_member

        mock_db.commit = Mock()

        with patch.object(team_service, "team_repo", mock_team_repo):
            with patch.object(team_service, "team_member_repo", mock_team_member_repo):
                result = team_service.update_member_role("team-id", "admin-id", "user-id", "ADMIN")

                assert result.role == "ADMIN"
                mock_db.commit.assert_called_once()

    def test_update_member_role_cannot_demote_last_admin(self, team_service):
        mock_team = Mock()
        mock_team.id = "team-id"

        mock_team_member = Mock()
        mock_team_member.role = "ADMIN"

        mock_team_repo = Mock()
        mock_team_repo.get.return_value = mock_team

        mock_team_member_repo = Mock()
        mock_team_member_repo.get.return_value = mock_team_member
        mock_team_member_repo.count_admins.return_value = 1
        mock_team_member_repo.get_by_user_and_team.return_value = mock_team_member

        with patch.object(team_service, "team_repo", mock_team_repo):
            with patch.object(team_service, "team_member_repo", mock_team_member_repo):
                with pytest.raises(TeamError):
                    team_service.update_member_role("team-id", "admin-id", "user-id", "MEMBER")
