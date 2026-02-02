"""
Export Service

Provides functionality to export transcripts in various formats:
- TXT: Plain text
- JSON: Structured JSON with metadata and segments
- SRT: SubRip subtitle format
- VTT: WebVTT subtitle format
"""
import json
from datetime import datetime
from typing import List, Dict, Any

from poly_db.models.transcripts import Transcript


def format_timestamp_ms(ms: int) -> str:
    """
    Format milliseconds to SRT/VTT timestamp format.
    
    Args:
        ms: Time in milliseconds
        
    Returns:
        Formatted timestamp string (HH:MM:SS,mmm for SRT or HH:MM:SS.mmm for VTT)
    """
    hours = ms // 3600000
    minutes = (ms % 3600000) // 60000
    seconds = (ms % 60000) // 1000
    milliseconds = ms % 1000
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def format_timestamp_ms_vtt(ms: int) -> str:
    """
    Format milliseconds to VTT timestamp format.
    
    Args:
        ms: Time in milliseconds
        
    Returns:
        Formatted timestamp string (HH:MM:SS.mmm)
    """
    hours = ms // 3600000
    minutes = (ms % 3600000) // 60000
    seconds = (ms % 60000) // 1000
    milliseconds = ms % 1000
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"


def export_txt(transcript: Transcript) -> str:
    """
    Export transcript as plain text.
    
    Args:
        transcript: The transcript to export
        
    Returns:
        Plain text string
    """
    return transcript.text


def export_json(transcript: Transcript) -> str:
    """
    Export transcript as JSON with metadata.
    
    Args:
        transcript: The transcript to export
        
    Returns:
        JSON string
    """
    data = {
        "id": str(transcript.id),
        "job_id": str(transcript.job_id),
        "text": transcript.text,
        "language": transcript.language,
        "segments": transcript.segments,
        "engine_version": transcript.engine_version,
        "created_at": transcript.created_at.isoformat() if transcript.created_at else None,
        "updated_at": transcript.updated_at.isoformat() if transcript.updated_at else None,
    }
    
    return json.dumps(data, indent=2, ensure_ascii=False)


def export_srt(transcript: Transcript) -> str:
    """
    Export transcript as SubRip (SRT) format.
    
    SRT Format:
    1
    00:00:00,000 --> 00:00:05,500
    Hello, welcome to the presentation.
    
    Args:
        transcript: The transcript to export
        
    Returns:
        SRT formatted string
    """
    segments = transcript.segments or []
    if not segments:
        return "WEBVTT\n"

    lines = []
    
    for idx, segment in enumerate(segments, start=1):
        start_ms = segment.get("start_ms", 0)
        end_ms = segment.get("end_ms", 0)
        text = segment.get("text", "").strip()
        speaker = segment.get("speaker")
        if speaker:
            text = f"{speaker}: {text}" if text else str(speaker)
        
        lines.append(str(idx))
        lines.append(f"{format_timestamp_ms(start_ms)} --> {format_timestamp_ms(end_ms)}")
        lines.append(text)
        lines.append("")  # Empty line between entries
    
    return "\n".join(lines)


def export_vtt(transcript: Transcript) -> str:
    """
    Export transcript as WebVTT (VTT) format.
    
    VTT Format:
    WEBVTT
    
    00:00:00.000 --> 00:00:05.500
    Hello, welcome to the presentation.
    
    Args:
        transcript: The transcript to export
        
    Returns:
        VTT formatted string
    """
    segments = transcript.segments or []
    lines = []
    
    # VTT header
    lines.append("WEBVTT")
    lines.append("")  # Empty line after header
    
    for segment in segments:
        start_ms = segment.get("start_ms", 0)
        end_ms = segment.get("end_ms", 0)
        text = segment.get("text", "").strip()
        
        lines.append(f"{format_timestamp_ms_vtt(start_ms)} --> {format_timestamp_ms_vtt(end_ms)}")
        lines.append(text)
        lines.append("")  # Empty line between entries
    
    return "\n".join(lines)


def export_transcript(
    transcript: Transcript,
    format: str = "txt",
) -> str:
    """
    Export transcript in the specified format.
    
    Args:
        transcript: The transcript to export
        format: Export format ("txt", "json", "srt", "vtt")
        
    Returns:
        Exported string in the requested format
        
    Raises:
        ValueError: If format is not supported
    """
    format = format.lower()
    
    if format == "txt":
        return export_txt(transcript)
    elif format == "json":
        return export_json(transcript)
    elif format == "srt":
        return export_srt(transcript)
    elif format == "vtt":
        return export_vtt(transcript)
    else:
        raise ValueError(f"Unsupported export format: {format}. Supported formats: txt, json, srt, vtt")


def get_export_filename(transcript: Transcript, format: str) -> str:
    """
    Generate a filename for the export.
    
    Args:
        transcript: The transcript being exported
        format: Export format extension
        
    Returns:
        Filename string
    """
    # Use job ID or transcript ID for filename
    base_name = str(transcript.job_id)[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    return f"transcript_{base_name}_{timestamp}.{format}"


class ExportService:
    """
    Service for managing transcript exports.
    """
    
    @staticmethod
    def export_transcript(
        transcript: Transcript,
        format: str = "txt",
    ) -> str:
        """
        Export a transcript in the specified format.
        
        Args:
            transcript: The transcript to export
            format: Export format ("txt", "json", "srt", "vtt")
            
        Returns:
            Exported string
        """
        return export_transcript(transcript, format)
    
    @staticmethod
    def get_export_content_type(format: str) -> str:
        """
        Get the content type for an export format.
        
        Args:
            format: Export format
            
        Returns:
            HTTP content type
        """
        content_types = {
            "txt": "text/plain",
            "json": "application/json",
            "srt": "text/plain",
            "vtt": "text/vtt",
        }
        
        return content_types.get(format.lower(), "application/octet-stream")
    
    @staticmethod
    def get_export_filename(transcript: Transcript, format: str) -> str:
        """
        Generate a filename for the export.
        
        Args:
            transcript: The transcript being exported
            format: Export format
            
        Returns:
            Filename string for Content-Disposition header
        """
        filename = get_export_filename(transcript, format)
        
        # Add Content-Disposition header-friendly format
        return f'attachment; filename="{filename}"'
