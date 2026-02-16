"""Pytest configuration for API tests."""

import sys
from pathlib import Path

# Add the parent directory (apps/api) to the path so 'main' can be imported
api_dir = Path(__file__).parent.parent
if str(api_dir) not in sys.path:
    sys.path.insert(0, str(api_dir))
