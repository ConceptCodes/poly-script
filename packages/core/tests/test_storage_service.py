"""Tests for StorageService."""

import os
from pathlib import Path
from unittest.mock import Mock, patch

from poly_core.services.storage_service import (
    LocalStorageBackend,
    S3StorageBackend,
    get_storage_backend,
)


class TestStorageBackendFactory:
    """Tests for storage backend factory function."""

    def test_get_local_storage_backend(self):
        """Verify local storage backend is created correctly."""
        with patch.dict(os.environ, {"STORAGE_PATH": "/tmp/uploads"}):
            backend = get_storage_backend(
                backend_type="local",
                storage_path="/tmp/uploads",
            )

            assert backend is not None
            assert isinstance(backend, LocalStorageBackend)

    def test_get_s3_storage_backend(self):
        """Verify S3 storage backend is created with correct credentials."""
        backend = get_storage_backend(
            backend_type="s3",
            bucket="test-bucket",
            region="us-east-1",
            access_key="test-key",
            secret_key="test-secret",
        )

        assert backend is not None
        assert isinstance(backend, S3StorageBackend)


class TestLocalStorageBackend:
    """Tests for LocalStorageBackend."""

    def test_initialization(self):
        """Verify local storage backend initializes correctly."""
        backend = LocalStorageBackend(storage_path="/tmp/uploads")

        assert backend.storage_path == Path("/tmp/uploads")

    def test_save_file(self):
        """Verify local storage save works correctly."""
        backend = LocalStorageBackend(storage_path="/tmp/uploads")

        with patch.object(Path, "mkdir"):
            mock_file = Mock()
            with patch("builtins.open") as mock_open:
                mock_open.return_value.__enter__ = Mock(return_value=mock_file)
                mock_open.return_value.__exit__ = Mock(return_value=False)

                result = backend.save(b"test content", "test.mp3")

                assert result is not None
                assert ".mp3" in result
                assert "local://" in result

    def test_get_url_local_file(self):
        """Verify local storage get_url works correctly."""
        backend = LocalStorageBackend(storage_path="/tmp/uploads")

        url = backend.get_url("local:///test/file.mp3")

        assert url is not None
        assert url == "/test/file.mp3"

    def test_delete_local_file(self):
        """Verify local storage delete works correctly."""
        backend = LocalStorageBackend(storage_path="/tmp/uploads")

        # Mock Path.exists to return True so unlink is called
        with (
            patch.object(Path, "exists", return_value=True),
            patch.object(Path, "unlink") as mock_unlink,
        ):
            backend.delete("local:///test/file.mp3")

            mock_unlink.assert_called_once()
