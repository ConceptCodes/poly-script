"""Pytest configuration for API tests."""

import sys
from pathlib import Path

api_dir = Path(__file__).parent.parent
api_dir_str = str(api_dir)

if api_dir_str in sys.path:
    sys.path.remove(api_dir_str)
sys.path.insert(0, api_dir_str)

worker_dir = str(Path(__file__).parent.parent.parent / "worker")
if worker_dir in sys.path:
    sys.path.remove(worker_dir)
