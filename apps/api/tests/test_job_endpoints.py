"""Tests for job status endpoints."""

import sys
from pathlib import Path

# Add apps/api to path before other imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import uuid
from datetime import UTC, datetime
from unittest.mock import Mock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from . import setup_paths as _setup_paths
from ..main import app

del _setup_paths

from poly_db.models import JobStatus


@pytest.fixture
async def client():
    """Test client for FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_team_id():
    """Sample team ID for testing."""
    return uuid.UUID("550e8400-e29b-41d4-a716-446655440000")


@pytest.fixture
def sample_job_id():
    """Sample job ID for testing."""
    return uuid.UUID("550e8400-e29b-41d4-a716-446655440001")


class TestJobListEndpoint:
    """Tests for GET /v1/jobs endpoint."""

    @pytest.mark.asyncio
    async def test_list_jobs_empty(self, client: AsyncClient, sample_team_id):
        """Test listing jobs when none exist."""
        with patch("src.dependencies.get_current_team_id") as mock_team:
            mock_team.return_value = sample_team_id

            with patch("db.repositories.TranscriptionJobRepository") as mock_repo_class:
                mock_repo = Mock()
                mock_repo_class.return_value = mock_repo
                mock_repo.get_by_team_id.return_value = []

                with patch("db.repositories.AudioAssetRepository") as mock_audio_repo_class:
                    mock_audio_repo = Mock()
                    mock_audio_repo_class.return_value = mock_audio_repo

                    response = await client.get(
                        "/v1/jobs",
                        headers={"Authorization": "Bearer test-token"},
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["jobs"] == []
                    assert data["total"] == 0
                    assert data["page"] == 1
                    assert data["page_size"] == 20

    @pytest.mark.asyncio
    async def test_list_jobs_with_data(self, client: AsyncClient, sample_team_id, sample_job_id):
        """Test listing jobs with sample data."""
        with patch("src.dependencies.get_current_team_id") as mock_team:
            mock_team.return_value = sample_team_id

            with patch("db.repositories.TranscriptionJobRepository") as mock_repo_class:
                mock_repo = Mock()
                mock_repo_class.return_value = mock_repo

                # Mock job
                mock_job = Mock()
                mock_job.id = sample_job_id
                mock_job.status = JobStatus.QUEUED
                mock_job.progress = 0
                mock_job.progress_stage = None
                mock_job.requested_language = "en"
                mock_job.created_at = datetime.now(UTC)
                mock_job.started_at = None
                mock_job.finished_at = None
                mock_repo.get_by_team_id.return_value = [mock_job]

                with patch("db.repositories.AudioAssetRepository") as mock_audio_repo_class:
                    mock_audio_repo = Mock()
                    mock_audio_repo_class.return_value = mock_audio_repo

                    # Mock audio
                    mock_audio = Mock()
                    mock_audio.filename = "test.mp3"
                    mock_audio_repo.get_by_job_id.return_value = mock_audio

                    response = await client.get(
                        "/v1/jobs",
                        headers={"Authorization": "Bearer test-token"},
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert len(data["jobs"]) == 1
                    assert data["jobs"][0]["id"] == str(sample_job_id)
                    assert data["jobs"][0]["status"] == "QUEUED"
                    assert data["jobs"][0]["filename"] == "test.mp3"
                    assert data["jobs"][0]["progress_pct"] == 0
                    assert data["total"] == 1

    @pytest.mark.asyncio
    async def test_list_jobs_with_status_filter(self, client: AsyncClient, sample_team_id):
        """Test listing jobs filtered by status."""
        with patch("src.dependencies.get_current_team_id") as mock_team:
            mock_team.return_value = sample_team_id

            with patch("db.repositories.TranscriptionJobRepository") as mock_repo_class:
                mock_repo = Mock()
                mock_repo_class.return_value = mock_repo
                mock_repo.get_by_team_id.return_value = []

                with patch("db.repositories.AudioAssetRepository") as mock_audio_repo_class:
                    mock_audio_repo_class.return_value = Mock()

                    response = await client.get(
                        "/v1/jobs?status=RUNNING",
                        headers={"Authorization": "Bearer test-token"},
                    )

                    assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_jobs_with_pagination(self, client: AsyncClient, sample_team_id):
        """Test listing jobs with pagination."""
        with patch("src.dependencies.get_current_team_id") as mock_team:
            mock_team.return_value = sample_team_id

            with patch("db.repositories.TranscriptionJobRepository") as mock_repo_class:
                mock_repo = Mock()
                mock_repo_class.return_value = mock_repo
                mock_repo.get_by_team_id.return_value = []

                with patch("db.repositories.AudioAssetRepository") as mock_audio_repo_class:
                    mock_audio_repo_class.return_value = Mock()

                    response = await client.get(
                        "/v1/jobs?page=2&page_size=10",
                        headers={"Authorization": "Bearer test-token"},
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["page"] == 2
                    assert data["page_size"] == 10


class TestJobDetailEndpoint:
    """Tests for GET /v1/jobs/:jobId endpoint."""

    @pytest.mark.asyncio
    async def test_get_job_success(self, client: AsyncClient, sample_team_id, sample_job_id):
        """Test getting job details successfully."""
        with patch("src.dependencies.get_current_team_id") as mock_team:
            mock_team.return_value = sample_team_id

            with patch("db.database.get_db_session") as mock_get_session:
                mock_session = Mock()
                mock_get_session.return_value.__enter__.return_value = mock_session

                with patch("db.repositories.TranscriptionJobRepository") as mock_repo_class:
                    mock_repo = Mock()
                    mock_repo_class.return_value = mock_repo

                    # Mock job
                    mock_job = Mock()
                    mock_job.id = sample_job_id
                    mock_job.team_id = sample_team_id
                    mock_job.status = JobStatus.RUNNING
                    mock_job.requested_language = "en"
                    mock_job.detected_language = None
                    mock_job.engine = "whisper-local"
                    mock_job.options = {}
                    mock_job.progress = 50
                    mock_job.progress_stage = "transcribing"
                    mock_job.attempts = 1
                    mock_job.error_code = None
                    mock_job.error_message = None
                    mock_job.created_at = datetime.now(UTC)
                    mock_job.started_at = datetime.now(UTC)
                    mock_job.finished_at = None
                    mock_repo.get.return_value = mock_job

                    with patch("db.repositories.AudioAssetRepository") as mock_audio_repo_class:
                        mock_audio_repo = Mock()
                        mock_audio_repo_class.return_value = mock_audio_repo
                        mock_audio.filename = "test.mp3"
                        mock_audio_repo.get_by_job_id.return_value = mock_audio

                        response = await client.get(
                            f"/v1/jobs/{sample_job_id}",
                            headers={"Authorization": "Bearer test-token"},
                        )

                        assert response.status_code == 200
                        data = response.json()
                        assert data["id"] == str(sample_job_id)
                        assert data["status"] == "RUNNING"
                        assert data["filename"] == "test.mp3"
                        assert data["progress_pct"] == 50
                        assert data["progress_stage"] == "transcribing"

    @pytest.mark.asyncio
    async def test_get_job_not_found(self, client: AsyncClient, sample_team_id, sample_job_id):
        """Test getting non-existent job returns 404."""
        with patch("src.dependencies.get_current_team_id") as mock_team:
            mock_team.return_value = sample_team_id

            with patch("db.database.get_db_session") as mock_get_session:
                mock_session = Mock()
                mock_get_session.return_value.__enter__.return_value = mock_session

                with patch("db.repositories.TranscriptionJobRepository") as mock_repo_class:
                    mock_repo = Mock()
                    mock_repo_class.return_value = mock_repo
                    mock_repo.get.return_value = None

                    response = await client.get(
                        f"/v1/jobs/{sample_job_id}",
                        headers={"Authorization": "Bearer test-token"},
                    )

                    assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_job_forbidden(self, client: AsyncClient, sample_team_id, sample_job_id):
        """Test getting job from different team returns 403."""
        other_team_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440002")

        with patch("src.dependencies.get_current_team_id") as mock_team:
            mock_team.return_value = other_team_id

            with patch("db.database.get_db_session") as mock_get_session:
                mock_session = Mock()
                mock_get_session.return_value.__enter__.return_value = mock_session

                with patch("db.repositories.TranscriptionJobRepository") as mock_repo_class:
                    mock_repo = Mock()
                    mock_repo_class.return_value = mock_repo

                    mock_job = Mock()
                    mock_job.id = sample_job_id
                    mock_job.team_id = sample_team_id  # Different from auth team
                    mock_repo.get.return_value = mock_job

                    response = await client.get(
                        f"/v1/jobs/{sample_job_id}",
                        headers={"Authorization": "Bearer test-token"},
                    )

                    assert response.status_code == 403
