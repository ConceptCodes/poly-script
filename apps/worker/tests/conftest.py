"""Worker tests configuration."""
import pytest
import os
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "storage" / "db"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "storage" / "poly-redis"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "core"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "stt"))

@pytest.fixture
def test_settings():
    """Test settings override."""
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["REDIS_URL"] = "redis://localhost:6379/1"
    os.environ["STORAGE_BACKEND"] = "local"
    os.environ["WHISPER_MODEL_SIZE"] = "tiny"
    return os.environ
