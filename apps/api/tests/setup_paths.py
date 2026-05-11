import sys
from pathlib import Path

tests_dir = Path(__file__).resolve().parent
api_root = tests_dir.parent
apps_dir = api_root.parent
src_dir = api_root / "src"

for candidate in (apps_dir, api_root, src_dir):
    candidate_str = str(candidate)
    if candidate_str not in sys.path:
        sys.path.insert(0, candidate_str)
