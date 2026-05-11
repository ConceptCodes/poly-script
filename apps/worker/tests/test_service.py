"""Tests for WorkerService."""

from unittest.mock import Mock, patch

import pytest
from apps.worker.src.service import WorkerService


@pytest.fixture
def mock_settings():
    """Mock settings."""
    with patch("apps.worker.src.service.get_settings") as mock_get_settings:
        mock_settings = Mock()
        mock_settings.QUEUE_MAX_RETRIES = 2
        mock_settings.QUEUE_RETRY_BACKOFF = 2
        mock_settings.STORAGE_BACKEND = "local"
        mock_settings.STORAGE_PATH = "./storage"
        mock_settings.STORAGE_MIN_FREE_BYTES = 0
        mock_settings.AWS_S3_BUCKET = None
        mock_settings.AWS_REGION = "us-east-1"
        mock_settings.AWS_ACCESS_KEY_ID = None
        mock_settings.AWS_SECRET_ACCESS_KEY = None
        mock_get_settings.return_value = mock_settings
        yield mock_settings


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    with patch("apps.worker.src.service.get_redis_client") as mock:
        mock.return_value = Mock()
        yield mock


@pytest.fixture
def mock_storage():
    """Mock storage backend."""
    with patch("apps.worker.src.service.get_storage_backend") as mock:
        mock.return_value = Mock()
        yield mock


@pytest.fixture
def mock_bootstrap():
    """Mock STT engine bootstrap."""
    with patch("apps.worker.src.service.initialize_engines"):
        yield


class TestWorkerService:
    """Tests for WorkerService."""

    @pytest.mark.usefixtures("mock_settings", "mock_redis", "mock_storage", "mock_bootstrap")
    def test_service_initialization(self):
        """Test service initializes correctly."""
        service = WorkerService()

        assert service._consumer is not None
        assert service._redis_client is not None
        assert service._queue is not None
        assert service._storage_backend is not None

    @pytest.mark.usefixtures("mock_settings", "mock_redis", "mock_storage", "mock_bootstrap")
    def test_start_service(self):
        """Test starting the service."""
        service = WorkerService()
        service.start()

        assert service.is_running

        service.stop()

    @pytest.mark.usefixtures("mock_settings", "mock_redis", "mock_storage", "mock_bootstrap")
    def test_stop_service(self):
        """Test stopping the service."""
        service = WorkerService()
        service.start()

        assert service.is_running

        service.stop()
        assert not service.is_running

    @pytest.mark.usefixtures("mock_settings", "mock_redis", "mock_storage", "mock_bootstrap")
    def test_current_job_id(self):
        """Test getting current job ID."""
        service = WorkerService()

        # Initially None
        assert service.current_job_id is None

        service.start()
        service.stop()
