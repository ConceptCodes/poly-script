"""Tests for transcript segment operations (split/merge/timestamps)."""
import pytest
from uuid import uuid4
from sqlalchemy.orm import Session

from poly_db.database import get_db_session
from poly_db.repositories import TranscriptRepository
from poly_core.services.transcript_service import TranscriptService



@pytest.fixture
def db():
    with get_db_session() as session:
        yield session


@pytest.fixture
def sample_transcript(db: Session):
    """Create a sample transcript for testing."""
    repo = TranscriptRepository(db)
    
    transcript_data = {
        "job_id": uuid4(),
        "text": "Sample transcript for testing",
        "language": "en",
        "segments": [
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
        "engine_version": "test-engine-v1",
    }
    
    from poly_db.models.transcripts import Transcript
    transcript = Transcript(**transcript_data)
    db.add(transcript)
    db.flush()
    
    return transcript


class TestSplitSegment:
    """Tests for segment split operation."""

    def test_split_segment_at_valid_timestamp(self, db: Session, sample_transcript):
        """Test splitting a segment at a valid timestamp."""
        service = TranscriptService(db)
        transcript_id = str(sample_transcript.id)
        
        updated, new_ids = service.split_segment(
            transcript_id=transcript_id,
            segment_id=0,
            user_id=str(uuid4()),
            split_at_ms=1500,
        )
        
        # Verify segment was split
        assert len(updated.segments) == 4
        assert new_ids == [0, 1]
        
        # Verify first segment was split
        first_segment = updated.segments[0]
        assert first_segment["start_ms"] == 0
        assert first_segment["end_ms"] == 1500
        assert first_segment["speaker"] == "Speaker 1"
        
        # Verify second segment was split
        second_segment = updated.segments[1]
        assert second_segment["start_ms"] == 1500
        assert second_segment["end_ms"] == 3000
        assert second_segment["speaker"] == "Speaker 1"
    
    def test_split_segment_invalid_timestamp(self, db: Session, sample_transcript):
        """Test splitting with timestamp outside segment range."""
        service = TranscriptService(db)
        transcript_id = str(sample_transcript.id)
        
        with pytest.raises(ValueError, match="split_at_ms.*must be between"):
            service.split_segment(
                transcript_id=transcript_id,
                segment_id=0,
                user_id=str(uuid4()),
                split_at_ms=5000,  # Outside range (0-3000)
            )
    
    def test_split_segment_invalid_id(self, db: Session, sample_transcript):
        """Test splitting non-existent segment."""
        service = TranscriptService(db)
        transcript_id = str(sample_transcript.id)
        
        with pytest.raises(ValueError, match="Invalid segment_id"):
            service.split_segment(
                transcript_id=transcript_id,
                segment_id=10,  # Doesn't exist
                user_id=str(uuid4()),
                split_at_ms=1500,
            )


class TestMergeSegments:
    """Tests for segment merge operation."""

    def test_merge_consecutive_segments(self, db: Session, sample_transcript):
        """Test merging two consecutive segments."""
        service = TranscriptService(db)
        transcript_id = str(sample_transcript.id)
        
        updated, merged_id, removed_ids = service.merge_segments(
            transcript_id=transcript_id,
            segment_ids=[0, 1],
            user_id=str(uuid4()),
        )
        
        # Verify segments were merged
        assert len(updated.segments) == 2
        assert merged_id == 0
        assert removed_ids == [1]
        
        # Verify merged segment content
        merged_segment = updated.segments[0]
        assert merged_segment["start_ms"] == 0
        assert merged_segment["end_ms"] == 6000
        assert "First segment of text" in merged_segment["text"]
        assert "Second segment of text" in merged_segment["text"]
        assert merged_segment["speaker"] == "Speaker 1"
    
    def test_merge_non_consecutive_segments_fails(self, db: Session, sample_transcript):
        """Test that merging non-consecutive segments fails."""
        service = TranscriptService(db)
        transcript_id = str(sample_transcript.id)
        
        with pytest.raises(ValueError, match="Segments must be consecutive"):
            service.merge_segments(
                transcript_id=transcript_id,
                segment_ids=[0, 2],  # Not consecutive
                user_id=str(uuid4()),
            )
    
    def test_merge_single_segment_fails(self, db: Session, sample_transcript):
        """Test that merging a single segment fails."""
        service = TranscriptService(db)
        transcript_id = str(sample_transcript.id)
        
        with pytest.raises(ValueError, match="At least 2 segments required"):
            service.merge_segments(
                transcript_id=transcript_id,
                segment_ids=[0],
                user_id=str(uuid4()),
            )


class TestUpdateSegmentTimestamps:
    """Tests for updating segment timestamps."""

    def test_update_timestamps(self, db: Session, sample_transcript):
        """Test updating segment timestamps."""
        service = TranscriptService(db)
        transcript_id = str(sample_transcript.id)
        
        updated = service.update_segment_timestamps(
            transcript_id=transcript_id,
            segment_id=1,
            user_id=str(uuid4()),
            start_ms=3500,
            end_ms=5500,
        )
        
        segment = updated.segments[1]
        assert segment["start_ms"] == 3500
        assert segment["end_ms"] == 5500
        assert segment["text"] == "Second segment of text"  # Text unchanged
    
    def test_update_invalid_timestamps(self, db: Session, sample_transcript):
        """Test that invalid timestamp updates fail."""
        service = TranscriptService(db)
        transcript_id = str(sample_transcript.id)
        
        # start_ms >= end_ms
        with pytest.raises(ValueError, match="start_ms must be less than end_ms"):
            service.update_segment_timestamps(
                transcript_id=transcript_id,
                segment_id=1,
                user_id=str(uuid4()),
                start_ms=5500,
                end_ms=3500,
            )
    
    def test_update_timestamps_overlap_previous(self, db: Session, sample_transcript):
        """Test that overlapping with previous segment fails."""
        service = TranscriptService(db)
        transcript_id = str(sample_transcript.id)
        
        with pytest.raises(ValueError, match="start_ms cannot overlap with previous segment"):
            service.update_segment_timestamps(
                transcript_id=transcript_id,
                segment_id=1,
                user_id=str(uuid4()),
                start_ms=2000,  # Overlaps with segment 0 (0-3000)
                end_ms=5500,
            )
