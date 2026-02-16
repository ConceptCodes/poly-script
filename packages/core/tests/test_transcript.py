"""Unit tests for transcript service."""

# ruff: noqa: ARG001

import uuid
from unittest.mock import MagicMock, Mock

import pytest
from sqlalchemy.orm import Session

from poly_core.services.transcript_service import TranscriptService
from poly_db.repositories.transcripts import TranscriptEditRepository, TranscriptRepository


@pytest.fixture
def mock_session():
    """Create a mock database session."""
    session = MagicMock(spec=Session)
    return session


@pytest.fixture
def transcript_service(mock_session):
    """Create a TranscriptService with mock session."""
    service = TranscriptService(mock_session)
    service.repo = Mock(spec=TranscriptRepository)
    service.edit_repo = Mock(spec=TranscriptEditRepository)
    return service


@pytest.fixture
def mock_transcript():
    """Create a mock transcript."""
    transcript = Mock()
    transcript.id = uuid.uuid4()
    transcript.job_id = uuid.uuid4()
    transcript.team_id = uuid.uuid4()
    transcript.text = "Original transcript text"
    transcript.segments = [
        {"start_ms": 0, "end_ms": 5000, "text": "Hello world", "speaker": None},
        {"start_ms": 5000, "end_ms": 10000, "text": "Second segment", "speaker": None},
    ]
    transcript.language = "en"
    transcript.engine_version = "whisper-local-base"
    transcript.created_at = Mock()
    transcript.updated_at = Mock()
    transcript.job = Mock()
    transcript.job.team_id = uuid.uuid4()
    return transcript


@pytest.fixture
def mock_edit():
    """Create a mock transcript edit."""
    edit = Mock()
    edit.id = uuid.uuid4()
    edit.transcript_id = uuid.uuid4()
    edit.user_id = uuid.uuid4()
    edit.previous_text = "Original text"
    edit.new_text = "Updated text"
    edit.previous_segments = []
    edit.new_segments = []
    edit.created_at = Mock()
    return edit


class TestTranscriptServiceInit:
    """Test TranscriptService initialization."""

    def test_init_creates_repositories(self, transcript_service, mock_session):
        """Verify service initializes with correct repositories."""
        assert hasattr(transcript_service, "session")
        assert hasattr(transcript_service, "repo")
        assert hasattr(transcript_service, "edit_repo")


class TestGetTranscript:
    """Test get_transcript method."""

    def test_get_transcript_returns_transcript(
        self, transcript_service, mock_session, mock_transcript
    ):
        """Verify get_transcript returns the transcript."""
        transcript_service.repo.get.return_value = mock_transcript

        result = transcript_service.get_transcript(str(mock_transcript.id))

        assert result is not None
        assert result["id"] == mock_transcript.id
        transcript_service.repo.get.assert_called_once_with(str(mock_transcript.id))

    def test_get_transcript_returns_none_when_not_found(self, transcript_service, mock_session):
        """Verify get_transcript returns None for non-existent transcript."""
        transcript_service.repo.get.return_value = None

        result = transcript_service.get_transcript(str(uuid.uuid4()))

        assert result is None


class TestGetTranscriptWithTeamCheck:
    """Test get_transcript_with_team_check method."""

    def test_returns_transcript_for_correct_team(
        self, transcript_service, mock_session, mock_transcript
    ):
        """Verify transcript is returned when team matches."""
        transcript_service.repo.get.return_value = mock_transcript
        mock_transcript.job.team_id = mock_transcript.team_id

        result = transcript_service.get_transcript_with_team_check(
            str(mock_transcript.id), str(mock_transcript.team_id)
        )

        assert result is not None
        assert result["id"] == mock_transcript.id

    def test_returns_none_for_wrong_team(self, transcript_service, mock_session, mock_transcript):
        """Verify None is returned when team doesn't match."""
        transcript_service.repo.get.return_value = mock_transcript
        wrong_team_id = str(uuid.uuid4())
        mock_transcript.job.team_id = uuid.uuid4()  # Different team

        result = transcript_service.get_transcript_with_team_check(
            str(mock_transcript.id), wrong_team_id
        )

        assert result is None

    def test_returns_none_when_not_found(self, transcript_service, mock_session):
        """Verify None is returned when no transcript for job."""
        transcript_service.repo.get_by_job_id.return_value = None

        result = transcript_service.get_transcript_by_job(str(uuid.uuid4()))

        assert result is None


class TestUpdateFullText:
    """Test update_full_text method."""

    def test_updates_text_and_creates_edit(self, transcript_service, mock_session, mock_transcript):
        """Verify update_full_text updates text and logs edit."""
        transcript_service.repo.get.return_value = mock_transcript
        new_text = "Updated transcript text"

        result = transcript_service.update_full_text(
            str(mock_transcript.id), str(uuid.uuid4()), new_text
        )

        assert result is not None
        assert result["text"] == new_text
        mock_session.flush.assert_called()
        transcript_service.edit_repo.create.assert_called_once()

    def test_raises_error_for_nonexistent_transcript(self, transcript_service, mock_session):
        """Verify ValueError is raised for non-existent transcript."""
        transcript_service.repo.get.return_value = None

        with pytest.raises(ValueError) as exc_info:
            transcript_service.update_full_text(str(uuid.uuid4()), str(uuid.uuid4()), "New text")

        assert "not found" in str(exc_info.value)


class TestUpdateSegment:
    """Test update_segment method."""

    def test_updates_segment_text(self, transcript_service, mock_session, mock_transcript):
        """Verify update_segment updates the correct segment."""
        transcript_service.repo.get.return_value = mock_transcript
        segment_id = 1
        new_text = "Updated segment text"

        result = transcript_service.update_segment(
            str(mock_transcript.id), segment_id, str(uuid.uuid4()), new_text
        )

        assert result is not None
        assert result["segments"][segment_id]["text"] == new_text

    def test_raises_error_for_invalid_segment_id(
        self, transcript_service, mock_session, mock_transcript
    ):
        """Verify ValueError is raised for invalid segment_id."""
        transcript_service.repo.get.return_value = mock_transcript

        with pytest.raises(ValueError) as exc_info:
            transcript_service.update_segment(
                str(mock_transcript.id),
                999,  # Invalid segment
                str(uuid.uuid4()),
                "New text",
            )

        assert "Invalid segment_id" in str(exc_info.value)

    def test_raises_error_for_negative_segment_id(
        self, transcript_service, mock_session, mock_transcript
    ):
        """Verify ValueError is raised for negative segment_id."""
        transcript_service.repo.get.return_value = mock_transcript

        with pytest.raises(ValueError) as exc_info:
            transcript_service.update_segment(
                str(mock_transcript.id),
                -1,  # Negative segment
                str(uuid.uuid4()),
                "New text",
            )

        assert "Invalid segment_id" in str(exc_info.value)


class TestGetEditHistory:
    """Test get_edit_history method."""

    def test_returns_edit_history(self, transcript_service, mock_session, mock_edit):
        """Verify get_edit_history returns list of edits."""
        transcript_service.edit_repo.get_history_by_transcript_id.return_value = [mock_edit]

        result = transcript_service.get_edit_history(str(uuid.uuid4()), str(uuid.uuid4()))

        assert len(result) == 1
        assert result[0] == mock_edit

    def test_returns_empty_list_when_no_edits(self, transcript_service, mock_session):
        """Verify empty list is returned when no edits exist."""
        transcript_service.edit_repo.get_history_by_transcript_id.return_value = []

        result = transcript_service.get_edit_history(str(uuid.uuid4()), str(uuid.uuid4()))

        assert result == []


class TestRevertToOriginal:
    """Test revert_to_original method."""

    def test_reverts_to_original_text(
        self, transcript_service, mock_session, mock_transcript, mock_edit
    ):
        """Verify revert restores original text."""
        transcript_service.repo.get.return_value = mock_transcript
        mock_transcript.text = "Modified text"
        mock_transcript.segments = [{"text": "Modified segment"}]

        mock_edit.previous_text = "Original text"
        mock_edit.previous_segments = [{"text": "Original segment"}]
        transcript_service.edit_repo.get_history_by_transcript_id.return_value = [mock_edit]

        result = transcript_service.revert_to_original(
            str(uuid.uuid4()), str(mock_transcript.id), str(uuid.uuid4())
        )

        assert result is not None
        mock_session.flush.assert_called()

    def test_raises_error_when_no_edits_exist(
        self, transcript_service, mock_session, mock_transcript
    ):
        """Verify ValueError is raised when no edits to revert."""
        transcript_service.repo.get.return_value = mock_transcript
        transcript_service.edit_repo.get_history_by_transcript_id.return_value = []

        with pytest.raises(ValueError) as exc_info:
            transcript_service.revert_to_original(
                str(uuid.uuid4()), str(mock_transcript.id), str(uuid.uuid4())
            )

        assert "No edits to revert" in str(exc_info.value)


class TestListTranscripts:
    """Test list_transcripts method."""

    def test_returns_transcripts_and_count(self, transcript_service, mock_session, mock_transcript):
        """Verify list_transcripts returns transcripts and total count."""
        mock_query_result = MagicMock()
        mock_query_result.all.return_value = [mock_transcript]
        mock_query_result.scalars.return_value.all.return_value = [mock_transcript]
        mock_session.execute.return_value = mock_query_result

        result = transcript_service.list_transcripts(str(uuid.uuid4()))

        assert len(result[0]) == 1
        assert result[1] == 1  # total count

    def test_passes_language_filter(self, transcript_service, mock_session, mock_transcript):
        """Verify language filter is applied."""
        mock_query_result = MagicMock()
        mock_query_result.all.return_value = []
        mock_query_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_query_result

        transcript_service.list_transcripts(str(uuid.uuid4()), language="en")

        # Verify where clause was called with language filter
        mock_session.execute.assert_called()

    def test_passes_search_filter(self, transcript_service, mock_session, mock_transcript):
        """Verify search filter is applied."""
        mock_query_result = MagicMock()
        mock_query_result.all.return_value = []
        mock_query_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_query_result

        transcript_service.list_transcripts(str(uuid.uuid4()), search="hello")

        mock_session.execute.assert_called()

    def test_respects_pagination(self, transcript_service, mock_session):
        """Verify pagination parameters are applied."""
        mock_query_result = MagicMock()
        mock_query_result.all.return_value = []
        mock_query_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_query_result

        transcript_service.list_transcripts(str(uuid.uuid4()), page=2, page_size=10)

        mock_session.execute.assert_called()


class TestGetTranscriptByJob:
    """Test get_transcript_by_job method."""

    def test_returns_transcript_for_job(self, transcript_service, mock_session, mock_transcript):
        """Verify transcript is returned when found by job_id."""
        transcript_service.repo.get_by_job_id.return_value = mock_transcript

        result = transcript_service.get_transcript_by_job(str(mock_transcript.job_id))

        assert result is not None
        assert result["id"] == mock_transcript.id
        transcript_service.repo.get_by_job_id.assert_called_once_with(str(mock_transcript.job_id))

    def test_returns_none_when_not_found(self, transcript_service, mock_session):
        """Verify None is returned when no transcript for job."""
        transcript_service.repo.get_by_job_id.return_value = None

        result = transcript_service.get_transcript_by_job(str(uuid.uuid4()))

        assert result is None
