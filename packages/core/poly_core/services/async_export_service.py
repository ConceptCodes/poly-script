"""
Async Export Service

Provides async transcript export with artifact caching and presigned URL support.
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from poly_db.models.transcripts import Transcript
from .export_service import ExportService, get_export_filename


class ExportArtifact:
    """Represents a cached export artifact."""
    def __init__(
        self,
        format: str,
        content: str = "",
        storage_uri: str | None = None,
        presigned_url: str | None = None,
        url_expires_at: str | None = None,
        content_length: int = 0,
        created_at: datetime | None = None,
    ):
        self.format = format
        self.content = content
        self.storage_uri = storage_uri
        self.presigned_url = presigned_url
        self.url_expires_at = url_expires_at
        self.content_length = content_length
        self.created_at = created_at


class AsyncExportService:
    """Service for async transcript export with artifact caching."""

    def __init__(self, db_session: Session | None = None):
        self.session = db_session

    def get_cached_export(
        self,
        transcript: Transcript,
        format: str,
    ) -> ExportArtifact | None:
        """Get cached export if available and not expired.

        Args:
            transcript: The transcript to check
            format: Export format ("txt", "json", "srt", "vtt")

        Returns:
            ExportArtifact if cached and valid, None otherwise
        """
        format_versions = transcript.format_versions or {}
        if format not in format_versions:
            return None

        artifact_data = format_versions[format]
        presigned_url = artifact_data.get("presigned_url")
        expires_at = artifact_data.get("url_expires_at")

        # Check if URL is still valid (presigned URLs typically expire after 1 hour)
        if expires_at:
            expire_dt = datetime.fromisoformat(expires_at)
            if datetime.now(timezone.utc) > expire_dt:
                # URL expired, need to regenerate
                return None

        return ExportArtifact(
            format=format,
            content="",  # Content is stored externally for large files
            storage_uri=artifact_data.get("storage_uri"),
            presigned_url=presigned_url,
            url_expires_at=expires_at,
            content_length=artifact_data.get("content_length", 0),
            created_at=datetime.fromisoformat(artifact_data["created_at"]) if artifact_data.get("created_at") else None,
        )

    def generate_and_cache_export(
        self,
        transcript: Transcript,
        format: str,
        storage_backend: Any | None = None,
    ) -> ExportArtifact:
        """Generate export and cache artifact.

        Args:
            transcript: The transcript to export
            format: Export format ("txt", "json", "srt", "vtt")
            storage_backend: Optional storage backend for large files


        Returns:
            ExportArtifact with URL or content
        """
        # Generate export content
        content = ExportService.export_transcript(transcript, format)
        content_length = len(content.encode("utf-8"))
        presigned_url = None
        storage_uri = None

        # For large exports (> 1MB), store externally
        if content_length > 1024 * 1024 and storage_backend:
            filename = get_export_filename(transcript, format)
            storage_uri = storage_backend.save(
                content.encode("utf-8"),
                filename,
                ExportService.get_export_content_type(format),
            )
            # Generate presigned URL
            presigned_url = storage_backend.get_url(storage_uri, expires_in=3600)

        # Update transcript with cached artifact info
        if not transcript.format_versions:
            transcript.format_versions = {}

        expires_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()

        transcript.format_versions[format] = {
            "storage_uri": storage_uri,
            "presigned_url": presigned_url,
            "url_expires_at": expires_at,
            "content_length": content_length,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        if self.session:
            self.session.flush()

        return ExportArtifact(
            format=format,
            content=content if content_length <= 1024 * 1024 else "",
            storage_uri=storage_uri,
            presigned_url=presigned_url,
            url_expires_at=expires_at,
            content_length=content_length,
        )

    def regenerate_presigned_url(
        self,
        transcript: Transcript,
        format: str,
        storage_backend: Any,
    ) -> ExportArtifact:
        """Regenerate presigned URL for cached export.

        Args:
            transcript: The transcript
            format: Export format
            storage_backend: Storage backend instance

        Returns:
            ExportArtifact with new presigned URL
        """
        format_versions = transcript.format_versions or {}
        if format not in format_versions:
            raise ValueError(f"No cached export found for format: {format}")

        artifact_data = format_versions[format]
        storage_uri = artifact_data.get("storage_uri")

        if not storage_uri:
            raise ValueError("Cannot regenerate URL for inline content")

        # Generate new presigned URL
        presigned_url = storage_backend.get_url(storage_uri, expires_in=3600)

        expires_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()

        # Update cache
        artifact_data["presigned_url"] = presigned_url
        artifact_data["url_expires_at"] = expires_at

        if self.session:
            self.session.flush()

        return ExportArtifact(
            format=format,
            content="",
            storage_uri=storage_uri,
            presigned_url=presigned_url,
            url_expires_at=expires_at,
            content_length=artifact_data.get("content_length", 0),
        )
