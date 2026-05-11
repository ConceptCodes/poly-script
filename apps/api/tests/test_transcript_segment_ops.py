"""Tests for transcript segment operations."""

from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest

from poly_core.services.transcript_service import TranscriptService


@pytest.fixture
def sample_transcript():
    """Create a sample transcript object for testing."""
    return SimpleNamespace(
        id=uuid4(),
        job_id=uuid4(),
        text="Sample transcript for testing",
        language="en",
        segments=[
            {
                "start_ms": 0,
                "end_ms": 3000,
                "text": "First segment of text",
                "speaker": "Speaker 1",
            },
            {
                "start_ms": 3000,
                "end_ms": 6000,
                "text": "Second segment of text",
                "speaker": "Speaker 1",
            },
            {
                "start_ms": 6000,
                "end_ms": 9000,
                "text": "Third segment of text",
                "speaker": "Speaker 2",
            },
        ],
        engine_version="test-engine-v1",
        created_at=None,
        updated_at=None,
    )


@pytest.fixture
def service(sample_transcript):
    """Create a TranscriptService with mocked persistence."""
    transcript_service = TranscriptService(Mock())
    transcript_service.repo = Mock()
    transcript_service.repo.get.return_value = sample_transcript
    transcript_service.edit_repo = Mock()
    return transcript_service


class TestSplitSegment:
    """Tests for segment split operation."""

    def test_split_segment_at_valid_timestamp(self, service, sample_transcript):
        """Test splitting a segment at a valid timestamp."""
        updated, new_ids = service.split_segment(
            transcript_id=str(sample_transcript.id),
            segment_id=0,
            user_id=str(uuid4()),
            split_at_ms=1500,
        )

        assert len(updated.segments) == 4
        assert new_ids == [0, 1]
        assert updated.segments[0]["start_ms"] == 0
        assert updated.segments[0]["end_ms"] == 1500
        assert updated.segments[1]["start_ms"] == 1500
        assert updated.segments[1]["end_ms"] == 3000

    def test_split_segment_invalid_timestamp(self, service, sample_transcript):
        """Test splitting with timestamp outside segment range."""
        with pytest.raises(ValueError, match="split_at_ms.*must be between"):
            service.split_segment(
                transcript_id=str(sample_transcript.id),
                segment_id=0,
                user_id=str(uuid4()),
                split_at_ms=5000,
            )

    def test_split_segment_invalid_id(self, service, sample_transcript):
        """Test splitting non-existent segment."""
        with pytest.raises(ValueError, match="Invalid segment_id"):
            service.split_segment(
                transcript_id=str(sample_transcript.id),
                segment_id=10,
                user_id=str(uuid4()),
                split_at_ms=1500,
            )


class TestMergeSegments:
    """Tests for segment merge operation."""

    def test_merge_consecutive_segments(self, service, sample_transcript):
        """Test merging two consecutive segments."""
        updated, merged_id, removed_ids = service.merge_segments(
            transcript_id=str(sample_transcript.id),
            segment_ids=[0, 1],
            user_id=str(uuid4()),
        )

        assert len(updated.segments) == 2
        assert merged_id == 0
        assert removed_ids == [1]
        assert updated.segments[0]["start_ms"] == 0
        assert updated.segments[0]["end_ms"] == 6000
        assert "First segment of text" in updated.segments[0]["text"]
        assert "Second segment of text" in updated.segments[0]["text"]
        assert updated.segments[0]["speaker"] == "Speaker 1"

    def test_merge_non_consecutive_segments_fails(self, service, sample_transcript):
        """Test that merging non-consecutive segments fails."""
        with pytest.raises(ValueError, match="Segments must be consecutive"):
            service.merge_segments(
                transcript_id=str(sample_transcript.id),
                segment_ids=[0, 2],
                user_id=str(uuid4()),
            )

    def test_merge_single_segment_fails(self, service, sample_transcript):
        """Test that merging a single segment fails."""
        with pytest.raises(ValueError, match="At least 2 segments required"):
            service.merge_segments(
                transcript_id=str(sample_transcript.id),
                segment_ids=[0],
                user_id=str(uuid4()),
            )


class TestUpdateSegmentTimestamps:
    """Tests for updating segment timestamps."""

    def test_update_timestamps(self, service, sample_transcript):
        """Test updating segment timestamps."""
        updated = service.update_segment_timestamps(
            transcript_id=str(sample_transcript.id),
            segment_id=1,
            user_id=str(uuid4()),
            start_ms=3500,
            end_ms=5500,
        )

        assert updated.segments[1]["start_ms"] == 3500
        assert updated.segments[1]["end_ms"] == 5500
        assert updated.segments[1]["text"] == "Second segment of text"

    def test_update_invalid_timestamps(self, service, sample_transcript):
        """Test that invalid timestamp updates fail."""
        with pytest.raises(ValueError, match="start_ms must be less than end_ms"):
            service.update_segment_timestamps(
                transcript_id=str(sample_transcript.id),
                segment_id=1,
                user_id=str(uuid4()),
                start_ms=5500,
                end_ms=3500,
            )

    def test_update_timestamps_overlap_previous(self, service, sample_transcript):
        """Test that overlapping with previous segment fails."""
        with pytest.raises(ValueError, match="start_ms cannot overlap with previous segment"):
            service.update_segment_timestamps(
                transcript_id=str(sample_transcript.id),
                segment_id=1,
                user_id=str(uuid4()),
                start_ms=2000,
                end_ms=5500,
            )
