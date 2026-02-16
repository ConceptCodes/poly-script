"""Tests for JobManagerService."""

import uuid
from unittest.mock import Mock, patch

import pytest
from sqlalchemy.orm import Session

from poly_core.services.job_manager import JobManagerService


@pytest.fixture
def mock_db():
    """Mock database session."""
    return Mock(spec=Session)


@pytest.fixture
def job_manager(mock_db):
    """Create a JobManagerService instance."""
    return JobManagerService(mock_db)


class TestJobManagerService:
    """Tests for JobManagerService."""

    def test_service_initialization(self, job_manager, mock_db):
        """Verify service initializes with correct repositories."""
        assert job_manager.db_session == mock_db
        assert hasattr(job_manager, "job_repo")
        assert hasattr(job_manager, "team_repo")
        assert hasattr(job_manager, "audio_repo")

    def test_check_plan_limits_free_plan(self, job_manager):
        """Verify plan limits are checked for FREE plan."""
        mock_team = Mock()
        mock_team.plan = Mock(value="FREE")
        mock_team.monthly_upload_count = 4

        mock_team_repo = Mock()
        mock_team_repo.get.return_value = mock_team

        with patch.object(job_manager, "team_repo", mock_team_repo):
            result = job_manager.check_plan_limits(str(uuid.uuid4()))

            assert result["within_limits"] is True
            assert result["remaining"] == 1

    def test_check_plan_limits_exceeded(self, job_manager):
        """Verify plan limits catch exceeded quota."""
        mock_team = Mock()
        mock_team.plan = Mock(value="FREE")
        mock_team.monthly_upload_count = 5

        mock_team_repo = Mock()
        mock_team_repo.get.return_value = mock_team

        with patch.object(job_manager, "team_repo", mock_team_repo):
            result = job_manager.check_plan_limits(str(uuid.uuid4()))

            assert result["within_limits"] is False

    def test_create_job_success(self, job_manager, mock_db):
        """Verify job creation succeeds with valid parameters."""
        mock_team = Mock()
        mock_team.id = uuid.uuid4()
        mock_team.plan = Mock(value="FREE")
        mock_team.monthly_upload_count = 0

        mock_team_repo = Mock()
        mock_team_repo.get.return_value = mock_team

        mock_job = Mock()
        mock_job.id = uuid.uuid4()
        mock_job_repo = Mock()
        mock_job_repo.create.return_value = mock_job

        mock_db.add = Mock()
        mock_db.commit = Mock()

        with patch.object(job_manager, "team_repo", mock_team_repo):
            with patch.object(job_manager, "job_repo", mock_job_repo):
                result = job_manager.create_job(
                    team_id=str(mock_team.id),
                    user_id=str(uuid.uuid4()),
                    audio_ref={"storage_key": "test.mp3"},
                    language="en",
                )

                assert result is not None
                mock_db.commit.assert_called()
