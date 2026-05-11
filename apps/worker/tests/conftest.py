"""Worker tests configuration."""

import os
import sys
from pathlib import Path

import pytest

# Add the repo root so tests import worker code through apps.worker.src,
# avoiding collisions with the API package's top-level src module.
repo_root = Path(__file__).resolve().parents[3]
repo_root_str = str(repo_root)
if repo_root_str not in sys.path:
    sys.path.insert(0, repo_root_str)


@pytest.fixture
def test_settings():
    """Test settings override."""
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["REDIS_URL"] = "redis://localhost:6379/1"
    os.environ["STORAGE_BACKEND"] = "local"
    os.environ["WHISPER_MODEL_SIZE"] = "tiny"
    return os.environ
