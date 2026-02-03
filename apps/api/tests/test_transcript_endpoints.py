"""Integration tests for transcript API endpoints."""

import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


@pytest.fixture
def mock_transcript_service():
    """Create a mock TranscriptService."""
    with patch("src.routes.transcripts.TranscriptService") as mock:
        yield mock


@pytest.fixture
def mock_db_session():
    """Mock database session."""
    with patch("src.routes.transcripts.get_db_session") as mock:
        yield mock


@pytest.fixture
def sample_transcript_id():
    """Generate a sample transcript ID."""
    return uuid.uuid4()


@pytest.fixture
def sample_team_id():
    """Generate a sample team ID."""
    return uuid.uuid4()


@pytest.fixture
def sample_user_id():
    """Generate a sample user ID."""
    return uuid.uuid4()


@pytest.fixture
def sample_transcript():
    """Create a sample transcript mock."""
    transcript = MagicMock()
    transcript.id = uuid.uuid4()
    transcript.job_id = uuid.uuid4()
    transcript.text = "Test transcript text"
    transcript.language = "en"
    transcript.segments = [
        {"start_ms": 0, "end_ms": 5000, "text": "Hello world", "speaker": None},
        {"start_ms": 5000, "end_ms": 10000, "text": "Second segment", "speaker": None},
    ]
    transcript.engine_version = "whisper-local-base"
    transcript.created_at = MagicMock()
    transcript.updated_at = MagicMock()
    transcript.job = MagicMock()
    transcript.job.team_id = uuid.uuid4()
    return transcript


@pytest.fixture
def mock_current_team_id(sample_team_id):
    """Mock current team ID dependency."""

    async def mock_get_current_team_id():
        return sample_team_id

    from src.routes.transcripts import get_current_team_id

    app.dependency_overrides[get_current_team_id] = mock_get_current_team_id
    yield sample_team_id
    app.dependency_overrides.clear()


@pytest.fixture
def mock_current_user_id(sample_user_id):
    """Mock current user ID dependency."""

    async def mock_get_current_user_id():
        return str(sample_user_id)

    from src.dependencies import get_current_user_id

    app.dependency_overrides[get_current_user_id] = mock_get_current_user_id
    yield str(sample_user_id)
    app.dependency_overrides.clear()


class TestListTranscriptsEndpoint:
    """Test GET /v1/transcripts endpoint."""

    def test_list_transcripts_empty(self, mock_current_team_id, mock_db_session):
        """Test listing transcripts when empty."""
        with patch("src.routes.transcripts.TranscriptService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.list_transcripts.return_value = ([], 0)

            response = client.get("/v1/transcripts")

            assert response.status_code == 200
            data = response.json()
            assert data["transcripts"] == []
            assert data["total"] == 0
            assert data["page"] == 1

    def test_list_transcripts_with_data(
        self, mock_current_team_id, mock_db_session, sample_transcript
    ):
        """Test listing transcripts with data."""
        with patch("src.routes.transcripts.TranscriptService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.list_transcripts.return_value = ([sample_transcript], 1)

            with patch("src.routes.transcripts.AudioAssetRepository") as mock_audio:
                mock_audio.return_value.get_by_job_id.return_value = MagicMock(filename="test.mp3")

                response = client.get("/v1/transcripts")

                assert response.status_code == 200
                data = response.json()
                assert len(data["transcripts"]) == 1
                assert data["total"] == 1

    def test_list_transcripts_with_pagination(self, mock_current_team_id, mock_db_session):
        """Test listing transcripts with pagination."""
        with patch("src.routes.transcripts.TranscriptService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.list_transcripts.return_value = ([], 100)

            response = client.get("/v1/transcripts?page=2&page_size=10")

            assert response.status_code == 200
            data = response.json()
            assert data["page"] == 2
            assert data["page_size"] == 10

    def test_list_transcripts_with_filters(self, mock_current_team_id, mock_db_session):
        """Test listing transcripts with filters."""
        with patch("src.routes.transcripts.TranscriptService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.list_transcripts.return_value = ([], 0)

            response = client.get("/v1/transcripts?language=en&search=hello")

            assert response.status_code == 200
            mock_instance.list_transcripts.assert_called_once_with(
                team_id=str(mock_current_team_id),
                language="en",
                search="hello",
                page=1,
                page_size=20,
            )


class TestGetTranscriptEndpoint:
    """Test GET /v1/transcripts/{transcript_id} endpoint."""

    def test_get_transcript_success(
        self, mock_current_team_id, sample_transcript_id, sample_transcript
    ):
        """Test getting a transcript successfully."""
        with patch("src.routes.transcripts.TranscriptRepository") as mock_repo:
            mock_instance = mock_repo.return_value
            mock_instance.get.return_value = sample_transcript
            sample_transcript.job.team_id = mock_current_team_id

            response = client.get(f"/v1/transcripts/{sample_transcript_id}")

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == str(sample_transcript.id)
            assert data["text"] == sample_transcript.text
            assert len(data["segments"]) == 2

    def test_get_transcript_not_found(self, mock_current_team_id, sample_transcript_id):
        """Test getting a non-existent transcript."""
        with patch("src.routes.transcripts.TranscriptRepository") as mock_repo:
            mock_instance = mock_repo.return_value
            mock_instance.get.return_value = None

            response = client.get(f"/v1/transcripts/{sample_transcript_id}")

            assert response.status_code == 404
            assert "not found" in response.json()["detail"]

    def test_get_transcript_forbidden(
        self, mock_current_team_id, sample_transcript_id, sample_transcript
    ):
        """Test getting transcript from another team."""
        with patch("src.routes.transcripts.TranscriptRepository") as mock_repo:
            mock_instance = mock_repo.return_value
            mock_instance.get.return_value = sample_transcript
            sample_transcript.job.team_id = uuid.uuid4()  # Different team

            response = client.get(f"/v1/transcripts/{sample_transcript_id}")

            assert response.status_code == 403
            assert "don't have access" in response.json()["detail"]


class TestUpdateTranscriptEndpoint:
    """Test PATCH /v1/transcripts/{transcript_id} endpoint."""

    def test_update_transcript_success(
        self, mock_current_team_id, mock_current_user_id, sample_transcript_id, sample_transcript
    ):
        """Test updating transcript text successfully."""
        with patch("src.routes.transcripts.get_transcript_with_team_check") as mock_get:
            mock_get.return_value = sample_transcript

            with patch("src.routes.transcripts.TranscriptService") as mock_service:
                mock_instance = mock_service.return_value
                mock_instance.update_full_text.return_value = sample_transcript

                response = client.patch(
                    f"/v1/transcripts/{sample_transcript_id}",
                    json={"text": "Updated transcript text"},
                )

                assert response.status_code == 200
                mock_instance.update_full_text.assert_called_once()

    def test_update_transcript_invalid_body(
        self, mock_current_team_id, mock_current_user_id, sample_transcript_id
    ):
        """Test updating transcript with invalid body."""
        response = client.patch(
            f"/v1/transcripts/{sample_transcript_id}",
            json={"text": ""},  # Empty text should fail validation
        )

        assert response.status_code == 422  # Validation error


class TestGetTranscriptSegmentsEndpoint:
    """Test GET /v1/transcripts/{transcript_id}/segments endpoint."""

    def test_get_segments_success(
        self, mock_current_team_id, sample_transcript_id, sample_transcript
    ):
        """Test getting transcript segments."""
        with patch("src.routes.transcripts.get_transcript_with_team_check") as mock_get:
            mock_get.return_value = sample_transcript

            response = client.get(f"/v1/transcripts/{sample_transcript_id}/segments")

            assert response.status_code == 200
            data = response.json()
            assert "segments" in data
            assert len(data["segments"]) == 2


class TestUpdateSegmentEndpoint:
    """Test PATCH /v1/transcripts/{transcript_id}/segments/{segment_id} endpoint."""

    def test_update_segment_success(
        self, mock_current_team_id, mock_current_user_id, sample_transcript_id, sample_transcript
    ):
        """Test updating a segment successfully."""
        with patch("src.routes.transcripts.get_transcript_with_team_check") as mock_get:
            mock_get.return_value = sample_transcript

            with patch("src.routes.transcripts.TranscriptService") as mock_service:
                mock_instance = mock_service.return_value
                mock_instance.update_segment.return_value = sample_transcript

                response = client.patch(
                    f"/v1/transcripts/{sample_transcript_id}/segments/0",
                    json={"text": "Updated segment text"},
                )

                assert response.status_code == 200

    def test_update_segment_not_found(
        self, mock_current_team_id, mock_current_user_id, sample_transcript_id
    ):
        """Test updating non-existent segment."""
        with patch("src.routes.transcripts.get_transcript_with_team_check") as mock_get:
            mock_get.return_value = None

            response = client.patch(
                f"/v1/transcripts/{sample_transcript_id}/segments/999",
                json={"text": "Updated text"},
            )

            assert response.status_code == 404


class TestGetTranscriptHistoryEndpoint:
    """Test GET /v1/transcripts/{transcript_id}/history endpoint."""

    def test_get_history_success(self, mock_current_team_id, sample_transcript_id):
        """Test getting transcript edit history."""
        with patch("src.routes.transcripts.get_transcript_with_team_check") as mock_get:
            mock_get.return_value = MagicMock()

            with patch("src.routes.transcripts.TranscriptService") as mock_service:
                mock_instance = mock_service.return_value
                mock_edit = MagicMock()
                mock_edit.id = uuid.uuid4()
                mock_edit.user_id = uuid.uuid4()
                mock_edit.previous_text = "Original"
                mock_edit.new_text = "Updated"
                mock_edit.previous_segments = None
                mock_edit.new_segments = None
                mock_instance.get_edit_history.return_value = [mock_edit]

                response = client.get(f"/v1/transcripts/{sample_transcript_id}/history")

                assert response.status_code == 200
                data = response.json()
                assert "edits" in data
                assert data["total"] == 1


class TestRevertTranscriptEndpoint:
    """Test POST /v1/transcripts/{transcript_id}/revert endpoint."""

    def test_revert_success(
        self, mock_current_team_id, mock_current_user_id, sample_transcript_id, sample_transcript
    ):
        """Test reverting transcript successfully."""
        with patch("src.routes.transcripts.get_transcript_with_team_check") as mock_get:
            mock_get.return_value = sample_transcript

            with patch("src.routes.transcripts.TranscriptService") as mock_service:
                mock_instance = mock_service.return_value
                mock_instance.revert_to_original.return_value = sample_transcript

                response = client.post(
                    f"/v1/transcripts/{sample_transcript_id}/revert",
                    json={"text": "Revert confirmation"},
                )

                assert response.status_code == 200
                assert "reverted" in response.json()["message"]

    def test_revert_no_edits(
        self, mock_current_team_id, mock_current_user_id, sample_transcript_id, sample_transcript
    ):
        """Test reverting transcript with no edits."""
        with patch("src.routes.transcripts.get_transcript_with_team_check") as mock_get:
            mock_get.return_value = sample_transcript

            with patch("src.routes.transcripts.TranscriptService") as mock_service:
                mock_instance = mock_service.return_value
                mock_instance.revert_to_original.side_effect = ValueError("No edits to revert")

                response = client.post(
                    f"/v1/transcripts/{sample_transcript_id}/revert",
                    json={"text": "Revert confirmation"},
                )

                assert response.status_code == 400
                assert "No edits" in response.json()["detail"]


class TestExportTranscriptEndpoint:
    """Test GET /v1/transcripts/{transcript_id}/export endpoint."""

    def test_export_txt(self, mock_current_team_id, sample_transcript_id, sample_transcript):
        """Test exporting transcript as TXT."""
        with patch("src.routes.transcripts.get_transcript_with_team_check") as mock_get:
            mock_get.return_value = sample_transcript

            with patch("src.routes.transcripts.ExportService") as mock_export:
                mock_export.export_transcript.return_value = "Test transcript text"
                mock_export.get_export_content_type.return_value = "text/plain"
                mock_export.get_export_filename.return_value = 'attachment; filename="test.txt"'

                response = client.get(f"/v1/transcripts/{sample_transcript_id}/export?format=txt")

                assert response.status_code == 200
                assert response.text == "Test transcript text"
                assert "text/plain" in response.headers["content-type"]

    def test_export_srt(self, mock_current_team_id, sample_transcript_id, sample_transcript):
        """Test exporting transcript as SRT."""
        with patch("src.routes.transcripts.get_transcript_with_team_check") as mock_get:
            mock_get.return_value = sample_transcript

            with patch("src.routes.transcripts.ExportService") as mock_export:
                mock_export.export_transcript.return_value = (
                    "1\n00:00:00,000 --> 00:00:05,000\nHello"
                )
                mock_export.get_export_content_type.return_value = "text/plain"
                mock_export.get_export_filename.return_value = 'attachment; filename="test.srt"'

                response = client.get(f"/v1/transcripts/{sample_transcript_id}/export?format=srt")

                assert response.status_code == 200
                assert "-->" in response.text

    def test_export_invalid_format(self, mock_current_team_id, sample_transcript_id):
        """Test exporting with invalid format."""
        response = client.get(f"/v1/transcripts/{sample_transcript_id}/export?format=invalid")

        # Should still work but use default or return error
        assert response.status_code in [200, 422, 400]
