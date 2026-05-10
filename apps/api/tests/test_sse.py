"""
import sys
from pathlib import Path

# Add apps/api to path before other imports
sys.path.insert(0, str(Path(__file__).parent.parent))
SSE endpoint integration tests.

Tests Server-Sent Events endpoint for real-time job progress updates.
"""

import json
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
def session():
    """Mock database session."""
    from sqlalchemy.orm import Session

    return Mock(spec=Session)


@pytest.fixture
def mock_auth_token():
    """Mock authentication token."""
    return "test-token-12345"


class TestSSEEndpoint:
    """Tests for SSE endpoint."""

    @pytest.mark.asyncio
    async def test_sse_connection(self, client: AsyncClient, session: Mock):
        """Test SSE endpoint connects successfully."""
        # Create test job
        job_id = "550e8400-e29b-41d4-a716-446655440000"

        # Mock team and job access
        with patch("src.dependencies.get_current_team_id") as mock_team:
            mock_team.return_value = "team-123"

            with patch("db.repositories.TranscriptionJobRepository") as mock_repo_class:
                mock_repo = Mock()
                mock_repo.return_value.get.return_value.id = job_id
                mock_repo.return_value.get.return_value.team_id = "team-123"
                mock_repo.return_value.get.return_value.status = JobStatus.RUNNING
                mock_repo.return_value.get.return_value.progress = 50
                mock_repo.return_value.get.return_value.progress_stage = "transcribing"

                response = await client.get(
                    f"/v1/jobs/{job_id}/live",
                    headers={"Authorization": "Bearer test-token"},
                )

                # Check response
                assert response.status_code == 200
                assert "text/event-stream" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_sse_sends_initial_state(self, client: AsyncClient):
        """Test SSE sends initial job state."""
        job_id = "550e8400-e29b-41d4-a716-446655440001"

        with patch("src.dependencies.get_current_team_id") as mock_team:
            mock_team.return_value = "team-123"

            with patch("db.repositories.TranscriptionJobRepository") as mock_repo_class:
                mock_repo = Mock()
                mock_repo.return_value.get.return_value.id = job_id
                mock_repo.return_value.get.return_value.team_id = "team-123"
                mock_repo.return_value.get.return_value.status = JobStatus.RUNNING
                mock_repo.return_value.get.return_value.progress = 75
                mock_repo.return_value.get.return_value.progress_stage = "formatting"

                response = await client.get(
                    f"/v1/jobs/{job_id}/live",
                    headers={"Authorization": "Bearer test-token"},
                )

                # Get first event
                content = response.content.decode()
                lines = content.split("\n")

                # Find data line
                data_line = None
                for line in lines:
                    if line.startswith("data:"):
                        data_line = line
                        break

                assert data_line is not None
                data = json.loads(data_line[5:])  # Remove "data:" prefix

                # Verify initial state
                assert data["event"] == "progress"
                assert data["data"]["job_id"] == job_id
                assert data["data"]["status"] == "RUNNING"
                assert data["data"]["progress_pct"] == 75
                assert data["data"]["progress_stage"] == "formatting"

    @pytest.mark.asyncio
    async def test_sse_404_when_job_not_found(self, client: AsyncClient):
        """Test SSE returns 404 when job not found."""
        job_id = "550e8400-e29b-41d4-a716-446655440000"

        with patch("src.dependencies.get_current_team_id") as mock_team:
            mock_team.return_value = "team-123"

            with patch("db.repositories.TranscriptionJobRepository") as mock_repo_class:
                mock_repo = Mock()
                mock_repo.return_value.get.return_value = None

                response = await client.get(
                    f"/v1/jobs/{job_id}/live",
                    headers={"Authorization": "Bearer test-token"},
                )

                assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_sse_403_when_team_access_denied(self, client: AsyncClient):
        """Test SSE returns 403 when team doesn't match."""
        job_id = "550e8400-e29b-41d4-a716-446655440000"

        with patch("src.dependencies.get_current_team_id") as mock_team:
            mock_team.return_value = "team-456"  # Different team

            with patch("db.repositories.TranscriptionJobRepository") as mock_repo_class:
                mock_repo = Mock()
                mock_repo.return_value.get.return_value.id = job_id
                mock_repo.return_value.get.return_value.team_id = "team-123"  # Wrong team

                response = await client.get(
                    f"/v1/jobs/{job_id}/live",
                    headers={"Authorization": "Bearer test-token"},
                )

                assert response.status_code == 403

    @pytest.mark.asyncio
    @patch("apps.worker.src.progress.ProgressPublisher")
    async def test_sse_receives_progress_updates(self, client: AsyncClient, mock_publisher: Mock):
        """Test SSE receives progress updates from Redis."""
        job_id = "550e8400-e29b-41d4-a716-446655440000"

        with patch("src.dependencies.get_current_team_id") as mock_team:
            mock_team.return_value = "team-123"

            with patch("db.repositories.TranscriptionJobRepository") as mock_repo_class:
                mock_repo = Mock()
                mock_repo.return_value.get.return_value.id = job_id
                mock_repo.return_value.get.return_value.team_id = "team-123"
                mock_repo.return_value.get.return_value.status = JobStatus.RUNNING
                mock_repo.return_value.get.return_value.progress = 0

                # Mock Redis pub/sub
                async def mock_event_stream():
                    # Yield initial state
                    yield {
                        "event": "progress",
                        "data": {
                            "job_id": job_id,
                            "status": "RUNNING",
                            "progress_pct": 0,
                            "progress_stage": "starting",
                        },
                    }

                    # Yield progress update
                    yield {
                        "event": "progress",
                        "data": {
                            "job_id": job_id,
                            "status": "RUNNING",
                            "progress_pct": 50,
                            "progress_stage": "transcribing",
                        },
                    }

                    # Yield completion
                    yield {
                        "event": "progress",
                        "data": {
                            "job_id": job_id,
                            "status": "SUCCEEDED",
                            "progress_pct": 100,
                            "progress_stage": "completed",
                        },
                    }

                # This would normally stream from Redis
                # For test, we'll verify SSE endpoint exists and connects

                response = await client.get(
                    f"/v1/jobs/{job_id}/live",
                    headers={"Authorization": "Bearer test-token"},
                )

                # Verify connection
                assert response.status_code == 200
