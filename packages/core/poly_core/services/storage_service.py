"""Storage service for audio file management.

Supports local filesystem and AWS S3 backends with a unified interface.
"""

import uuid
from pathlib import Path
from typing import Protocol, runtime_checkable
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError


@runtime_checkable
class StorageBackend(Protocol):
    """Protocol for storage backends (local, S3)."""

    def save(
        self, file_content: bytes, filename: str, _content_type: str = "audio/mpeg"
    ) -> str:
        """Save file and return storage URI.

        Args:
            file_content: File bytes to save
            filename: Original filename
            content_type: MIME type of file

        Returns:
            Storage URI (e.g., 'local://path/to/file.mp3' or 's3://bucket/key.mp3')
        """
        ...

    def get_url(self, storage_uri: str, _expires_in: int = 3600) -> str:
        """Get accessible URL for file.

        Args:
            storage_uri: Storage URI from save()
            expires_in: URL expiry time in seconds (S3 only)

        Returns:
            Accessible URL
        """
        ...

    def delete(self, storage_uri: str) -> None:
        """Delete file by storage URI.

        Args:
            storage_uri: Storage URI from save()
        """
        ...


class LocalStorageBackend:
    """Local filesystem storage backend."""

    def __init__(self, storage_path: str = "./storage"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def save(
        self, file_content: bytes, filename: str, _content_type: str = "audio/mpeg"
    ) -> str:
        file_extension = Path(filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = self.storage_path / unique_filename

        with file_path.open("wb") as f:
            f.write(file_content)

        return f"local://{file_path}"

    def get_url(self, storage_uri: str, expires_in: int = 3600) -> str:
        parsed = urlparse(storage_uri)
        if parsed.scheme != "local":
            raise ValueError(f"Invalid storage URI scheme: {parsed.scheme}")
        return parsed.path

    def delete(self, storage_uri: str) -> None:
        parsed = urlparse(storage_uri)
        if parsed.scheme != "local":
            raise ValueError(f"Invalid storage URI scheme: {parsed.scheme}")

        file_path = Path(parsed.path)
        if file_path.exists():
            file_path.unlink()


class S3StorageBackend:
    """AWS S3 storage backend."""

    def __init__(self, bucket: str, region: str, access_key: str, secret_key: str):
        self.bucket = bucket
        self.s3_client = boto3.client(
            "s3",
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

    def save(self, file_content: bytes, filename: str, content_type: str = "audio/mpeg") -> str:
        file_extension = Path(filename).suffix
        unique_key = f"audio/{uuid.uuid4()}{file_extension}"

        try:
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=unique_key,
                Body=file_content,
                ContentType=content_type,
            )
        except ClientError as e:
            raise RuntimeError(f"Failed to upload to S3: {e}") from e

        return f"s3://{self.bucket}/{unique_key}"

    def get_url(self, storage_uri: str, expires_in: int = 3600) -> str:
        parsed = urlparse(storage_uri)
        if parsed.scheme != "s3":
            raise ValueError(f"Invalid storage URI scheme: {parsed.scheme}")

        bucket = parsed.netloc
        key = parsed.path.lstrip("/")

        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket, "Key": key},
                ExpiresIn=expires_in,
            )
            return url
        except ClientError as e:
            raise RuntimeError(f"Failed to generate presigned URL: {e}") from e

    def delete(self, storage_uri: str) -> None:
        parsed = urlparse(storage_uri)
        if parsed.scheme != "s3":
            raise ValueError(f"Invalid storage URI scheme: {parsed.scheme}")

        bucket = parsed.netloc
        key = parsed.path.lstrip("/")

        try:
            self.s3_client.delete_object(Bucket=bucket, Key=key)
        except ClientError as e:
            raise RuntimeError(f"Failed to delete from S3: {e}") from e


def get_storage_backend(  # noqa: PLR0913
    backend_type: str,
    storage_path: str = "./storage",
    bucket: str | None = None,
    region: str = "us-east-1",
    access_key: str | None = None,
    secret_key: str | None = None,
) -> StorageBackend:
    """Factory function to get storage backend instance.

    Args:
        backend_type: 'local' or 's3'
        storage_path: Local storage path (for local backend)
        bucket: S3 bucket name (for S3 backend)
        region: AWS region (for S3 backend)
        access_key: AWS access key (for S3 backend)
        secret_key: AWS secret key (for S3 backend)

    Returns:
        StorageBackend instance

    Raises:
        ValueError: If backend_type is invalid
    """
    if backend_type == "local":
        return LocalStorageBackend(storage_path=storage_path)
    elif backend_type == "s3":
        if not bucket or not access_key or not secret_key:
            raise ValueError("S3 backend requires bucket, access_key, and secret_key")
        return S3StorageBackend(
            bucket=bucket, region=region, access_key=access_key, secret_key=secret_key
        )
    else:
        raise ValueError(f"Invalid storage backend type: {backend_type}")
