"""Tests for ProgressPublisher."""
import pytest
from unittest.mock import Mock, patch

from src.progress import ProgressPublisher


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    return Mock()


@pytest.fixture
def publisher(mock_redis):
    """Create a ProgressPublisher instance."""
    with patch('src.progress.get_redis_client', return_value=mock_redis):
        return ProgressPublisher()


class TestProgressPublisher:
    """Tests for ProgressPublisher."""

    def test_publish_progress(self, publisher, mock_redis):
        """Test publishing progress updates."""
        publisher.publish_progress(
            job_id="test-job",
            team_id="test-team",
            progress_pct=50,
            progress_stage="transcribing",
            status="RUNNING",
        )
        
        mock_redis.publish.assert_called_once()
        call_args = mock_redis.publish.call_args[0]
        
        assert call_args[0] == "job:test-job:progress"
        
        import json
        payload = json.loads(call_args[1])
        assert payload["job_id"] == "test-job"
        assert payload["team_id"] == "test-team"
        assert payload["progress_pct"] == 50
        assert payload["progress_stage"] == "transcribing"
        assert payload["status"] == "RUNNING"

    def test_publish_stage_complete(self, publisher, mock_redis):
        """Test publishing stage completion."""
        publisher.publish_stage_complete(
            job_id="test-job",
            team_id="test-team",
            stage="transcribing",
        )
        
        mock_redis.publish.assert_called_once()
        call_args = mock_redis.publish.call_args[0]
        
        import json
        payload = json.loads(call_args[1])
        assert payload["progress_pct"] == 90  # transcribing stage progress
        assert payload["progress_stage"] == "transcribing"

    def test_get_stage_progress(self):
        """Test stage progress percentages."""
        assert ProgressPublisher._get_stage_progress("starting") == 0
        assert ProgressPublisher._get_stage_progress("downloading") == 10
        assert ProgressPublisher._get_stage_progress("decoding") == 20
        assert ProgressPublisher._get_stage_progress("transcribing") == 90
        assert ProgressPublisher._get_stage_progress("formatting") == 95
        assert ProgressPublisher._get_stage_progress("translating") == 98
        assert ProgressPublisher._get_stage_progress("saving") == 100
        assert ProgressPublisher._get_stage_progress("completed") == 100
        assert ProgressPublisher._get_stage_progress("failed") == 0
        assert ProgressPublisher._get_stage_progress("canceled") == 0


    def test_publish_progress_with_error(self, publisher, mock_redis):
        """Test publishing progress with error."""
        publisher.publish_progress(
            job_id="test-job",
            team_id="test-team",
            progress_pct=0,
            progress_stage="failed",
            status="FAILED",
            error_message="Test error",
        )
        
        mock_redis.publish.assert_called_once()
        call_args = mock_redis.publish.call_args[0]
        
        import json
        payload = json.loads(call_args[1])
        assert payload["status"] == "FAILED"
        assert payload["error_message"] == "Test error"
