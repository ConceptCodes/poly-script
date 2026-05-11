"""SSE endpoint tests for real-time job progress updates."""

import uuid
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from poly_db.models import JobStatus
from src.routes.jobs import get_current_team_id

from ..main import app
from . import setup_paths as _setup_paths

del _setup_paths


TEAM_ID = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
OTHER_TEAM_ID = uuid.UUID("550e8400-e29b-41d4-a716-446655440001")
JOB_ID = uuid.UUID("550e8400-e29b-41d4-a716-446655440010")


@pytest.fixture
async def client():
    """Test client for FastAPI app."""
    original_overrides = app.dependency_overrides.copy()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides = original_overrides


def override_team(team_id: uuid.UUID) -> None:
    app.dependency_overrides[get_current_team_id] = lambda: team_id


def job(**overrides):
    values = {
        "id": JOB_ID,
        "team_id": TEAM_ID,
        "status": JobStatus.RUNNING,
        "progress": 50,
        "progress_stage": "transcribing",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


async def empty_streamer(*_args, **_kwargs):
    if False:
        yield {}


async def one_update_streamer(*_args, **_kwargs):
    yield {
        "event": "progress",
        "data": {
            "job_id": str(JOB_ID),
            "status": "RUNNING",
            "progress_pct": 75,
            "progress_stage": "formatting",
        },
    }


class TestSSEEndpoint:
    """Tests for SSE endpoint."""

    @pytest.mark.asyncio
    async def test_sse_connection(self, client: AsyncClient):
        """Test SSE endpoint connects successfully."""
        override_team(TEAM_ID)

        with patch("src.routes.jobs.get_db_session") as db_session:
            db_session.return_value.__enter__.return_value = Mock()
            with patch("src.routes.jobs.TranscriptionJobRepository") as repo_class:
                repo_class.return_value.get_by_id.return_value = job()
                with patch("src.routes.jobs.job_progress_streamer", empty_streamer):
                    response = await client.get(f"/v1/jobs/{JOB_ID}/live")

        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_sse_sends_initial_state(self, client: AsyncClient):
        """Test SSE sends the current job state before waiting for Redis updates."""
        override_team(TEAM_ID)

        with patch("src.routes.jobs.get_db_session") as db_session:
            db_session.return_value.__enter__.return_value = Mock()
            with patch("src.routes.jobs.TranscriptionJobRepository") as repo_class:
                repo_class.return_value.get_by_id.return_value = job(
                    progress=75,
                    progress_stage="formatting",
                )
                with patch("src.routes.jobs.job_progress_streamer", empty_streamer):
                    response = await client.get(f"/v1/jobs/{JOB_ID}/live")

        assert response.status_code == 200
        content = response.text
        assert "event: progress" in content
        assert str(JOB_ID) in content
        assert "RUNNING" in content
        assert "75" in content
        assert "formatting" in content

    @pytest.mark.asyncio
    async def test_sse_404_when_job_not_found(self, client: AsyncClient):
        """Test SSE returns 404 when job not found."""
        override_team(TEAM_ID)

        with patch("src.routes.jobs.get_db_session") as db_session:
            db_session.return_value.__enter__.return_value = Mock()
            with patch("src.routes.jobs.TranscriptionJobRepository") as repo_class:
                repo_class.return_value.get_by_id.return_value = None
                response = await client.get(f"/v1/jobs/{JOB_ID}/live")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_sse_403_when_team_access_denied(self, client: AsyncClient):
        """Test SSE returns 403 when team doesn't match."""
        override_team(OTHER_TEAM_ID)

        with patch("src.routes.jobs.get_db_session") as db_session:
            db_session.return_value.__enter__.return_value = Mock()
            with patch("src.routes.jobs.TranscriptionJobRepository") as repo_class:
                repo_class.return_value.get_by_id.return_value = job()
                response = await client.get(f"/v1/jobs/{JOB_ID}/live")

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_sse_receives_progress_updates(self, client: AsyncClient):
        """Test SSE includes progress updates yielded by the stream generator."""
        override_team(TEAM_ID)

        with patch("src.routes.jobs.get_db_session") as db_session:
            db_session.return_value.__enter__.return_value = Mock()
            with patch("src.routes.jobs.TranscriptionJobRepository") as repo_class:
                repo_class.return_value.get_by_id.return_value = job(progress=0)
                with patch("src.routes.jobs.job_progress_streamer", one_update_streamer):
                    response = await client.get(f"/v1/jobs/{JOB_ID}/live")

        assert response.status_code == 200
        assert "formatting" in response.text
        assert "75" in response.text
