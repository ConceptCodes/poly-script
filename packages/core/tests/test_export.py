"""Unit tests for export service."""

import json
import uuid
from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from poly_core.services.export_service import (
    ExportService,
    export_json,
    export_srt,
    export_transcript,
    export_txt,
    export_vtt,
    format_timestamp_ms,
    format_timestamp_ms_vtt,
)


@pytest.fixture
def mock_transcript():
    """Create a mock transcript object."""
    transcript = Mock()
    transcript.id = uuid.uuid4()
    transcript.job_id = uuid.uuid4()
    transcript.text = "Hello, welcome to the presentation. Today we'll discuss the new features."
    transcript.language = "en"
    transcript.segments = [
        {
            "start_ms": 0,
            "end_ms": 5500,
            "text": "Hello, welcome to the presentation.",
            "speaker": None,
        },
        {
            "start_ms": 5500,
            "end_ms": 10200,
            "text": "Today we'll discuss the new features.",
            "speaker": None,
        },
    ]
    transcript.engine_version = "whisper-local-base"
    transcript.created_at = datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC)
    transcript.updated_at = datetime(2024, 1, 15, 11, 0, 0, tzinfo=UTC)
    return transcript


class TestTimestampFormatting:
    """Test timestamp formatting functions."""

    def test_format_timestamp_ms_srt(self):
        """Test SRT timestamp formatting (HH:MM:SS,mmm)."""
        assert format_timestamp_ms(0) == "00:00:00,000"
        assert format_timestamp_ms(5500) == "00:00:05,500"
        assert format_timestamp_ms(3600000) == "01:00:00,000"
        assert format_timestamp_ms(3661000) == "01:01:01,000"

    def test_format_timestamp_ms_vtt(self):
        """Test VTT timestamp formatting (HH:MM:SS.mmm)."""
        assert format_timestamp_ms_vtt(0) == "00:00:00.000"
        assert format_timestamp_ms_vtt(5500) == "00:00:05.500"
        assert format_timestamp_ms_vtt(3600000) == "01:00:00.000"
        assert format_timestamp_ms_vtt(3661000) == "01:01:01.000"


class TestExportTxt:
    """Test TXT export functionality."""

    def test_export_txt_returns_plain_text(self, mock_transcript):
        """Verify export_txt returns the transcript text as-is."""
        result = export_txt(mock_transcript)
        assert result == mock_transcript.text
        assert isinstance(result, str)


class TestExportJson:
    """Test JSON export functionality."""

    def test_export_json_returns_valid_json(self, mock_transcript):
        """Verify export_json returns valid JSON string."""
        result = export_json(mock_transcript)

        # Should be valid JSON
        data = json.loads(result)

        # Should contain expected fields
        assert data["id"] == str(mock_transcript.id)
        assert data["job_id"] == str(mock_transcript.job_id)
        assert data["text"] == mock_transcript.text
        assert data["language"] == mock_transcript.language
        assert data["segments"] == mock_transcript.segments
        assert data["engine_version"] == mock_transcript.engine_version


class TestExportSrt:
    """Test SRT export functionality."""

    def test_export_srt_format(self, mock_transcript):
        """Verify SRT export follows SubRip format."""
        result = export_srt(mock_transcript)
        lines = result.split("\n")

        # SRT format: index, timestamp line, text, empty line
        assert lines[0] == "1"
        assert "-->" in lines[1]
        assert lines[2] == "Hello, welcome to the presentation."
        assert lines[3] == ""  # Empty line between entries
        assert lines[4] == "2"
        assert "-->" in lines[5]
        assert lines[6] == "Today we'll discuss the new features."

    def test_export_srt_timestamps(self, mock_transcript):
        """Verify SRT timestamps are formatted correctly."""
        result = export_srt(mock_transcript)

        # First segment: 0ms -> 5500ms
        assert "00:00:00,000 --> 00:00:05,500" in result
        # Second segment: 5500ms -> 10200ms
        assert "00:00:05,500 --> 00:00:10,200" in result


class TestExportVtt:
    """Test VTT export functionality."""

    def test_export_vtt_format(self, mock_transcript):
        """Verify VTT export follows WebVTT format."""
        result = export_vtt(mock_transcript)
        lines = result.split("\n")

        # VTT format: WEBVTT header, empty line, timestamp line, text
        assert lines[0] == "WEBVTT"
        assert lines[1] == ""  # Empty line after header
        assert "-->" in lines[2]
        assert lines[3] == "Hello, welcome to the presentation."

    def test_export_vtt_timestamps(self, mock_transcript):
        """Verify VTT timestamps are formatted correctly."""
        result = export_vtt(mock_transcript)

        # VTT uses dot instead of comma
        assert "00:00:00.000 --> 00:00:05.500" in result


class TestExportTranscript:
    """Test the main export_transcript function."""

    def test_export_txt_format(self, mock_transcript):
        """Verify txt format works."""
        result = export_transcript(mock_transcript, "txt")
        assert result == mock_transcript.text

    def test_export_json_format(self, mock_transcript):
        """Verify json format works."""
        result = export_transcript(mock_transcript, "json")
        assert "whisper-local-base" in result

    def test_export_srt_format(self, mock_transcript):
        """Verify srt format works."""
        result = export_transcript(mock_transcript, "srt")
        assert "WEBVTT" not in result  # Not VTT format
        assert "-->" in result

    def test_export_vtt_format(self, mock_transcript):
        """Verify vtt format works."""
        result = export_transcript(mock_transcript, "vtt")
        assert result.startswith("WEBVTT")

    def test_export_unsupported_format_raises_error(self, mock_transcript):
        """Verify unsupported format raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            export_transcript(mock_transcript, "pdf")

        assert "Unsupported export format" in str(exc_info.value)
        assert "pdf" in str(exc_info.value)


class TestExportService:
    """Test the ExportService class."""

    def test_export_transcript_static_method(self, mock_transcript):
        """Verify ExportService.export_transcript works."""
        result = ExportService.export_transcript(mock_transcript, "txt")
        assert result == mock_transcript.text

    def test_get_export_content_type_txt(self):
        """Verify TXT content type is text/plain."""
        assert ExportService.get_export_content_type("txt") == "text/plain"

    def test_get_export_content_type_json(self):
        """Verify JSON content type is application/json."""
        assert ExportService.get_export_content_type("json") == "application/json"

    def test_get_export_content_type_srt(self):
        """Verify SRT content type is text/plain."""
        assert ExportService.get_export_content_type("srt") == "text/plain"

    def test_get_export_content_type_vtt(self):
        """Verify VTT content type is text/vtt."""
        assert ExportService.get_export_content_type("vtt") == "text/vtt"

    def test_get_export_filename(self, mock_transcript):
        """Verify export filename generation."""
        filename = ExportService.get_export_filename(mock_transcript, "txt")
        assert "transcript_" in filename
        assert ".txt" in filename

    def test_get_export_filename_contains_attachment(self, mock_transcript):
        """Verify filename includes Content-Disposition header format."""
        filename = ExportService.get_export_filename(mock_transcript, "json")
        assert filename.startswith("attachment; filename=")


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_segments(self):
        """Test export with empty segments list."""
        mock_transcript = Mock()
        mock_transcript.text = "Test"
        mock_transcript.segments = []

        result = export_srt(mock_transcript)
        # Should still return WEBVTT header
        assert result == "WEBVTT\n"

    def test_single_segment(self):
        """Test export with single segment."""
        mock_transcript = Mock()
        mock_transcript.text = "Single segment"
        mock_transcript.segments = [
            {"start_ms": 0, "end_ms": 1000, "text": "Single segment", "speaker": None}
        ]

        result = export_srt(mock_transcript)
        lines = result.split("\n")
        # Should have: index, timestamp, text (3 lines, no trailing empty line)
        assert len(lines) >= 3
        assert lines[0] == "1"

    def test_segments_with_speakers(self):
        """Test export with speaker labels."""
        mock_transcript = Mock()
        mock_transcript.text = "Hello"
        mock_transcript.segments = [
            {"start_ms": 0, "end_ms": 1000, "text": "Hello", "speaker": "Speaker 1"}
        ]

        # Speaker info should be in the text
        result = export_srt(mock_transcript)
        assert "Speaker 1" in result
