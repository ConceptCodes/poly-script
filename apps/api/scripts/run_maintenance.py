#!/usr/bin/env python3
"""Run periodic maintenance tasks (cron-friendly).

Tasks:
- Reset monthly billing usage
- Cleanup expired tokens/invitations
- Cleanup soft-deleted users
"""

import logging
import pathlib
import sys


def _setup_python_path():
    script_dir = pathlib.Path(__file__).resolve()
    repo_root = script_dir.parent.parent.parent
    core_path = repo_root / "packages" / "core"
    storage_path = repo_root / "packages" / "storage" / "db"
    if core_path.exists():
        sys.path.insert(0, str(core_path))
    if storage_path.exists():
        sys.path.insert(0, str(storage_path))


_setup_python_path()

from apps.api.src.config import get_settings  # noqa: E402

from poly_core.tasks.billing_tasks import reset_monthly_usage  # noqa: E402
from poly_core.tasks.cleanup_tasks import (  # noqa: E402
    cleanup_expired_invitations,
    cleanup_expired_password_resets,
    cleanup_revoked_tokens,
    cleanup_soft_deleted_users,
)
from poly_db.database import get_db_session  # noqa: E402

logger = logging.getLogger(__name__)


def main() -> int:
    logging.basicConfig(level=logging.INFO)
    settings = get_settings()
    grace_days = settings.DELETION_GRACE_PERIOD_DAYS

    with get_db_session() as session:
        results = []
        results.append(reset_monthly_usage(session))
        results.append(cleanup_expired_password_resets(session))
        results.append(cleanup_expired_invitations(session))
        results.append(cleanup_revoked_tokens(session))
        results.append(cleanup_soft_deleted_users(session, grace_days=grace_days))

    for item in results:
        logger.info("Maintenance task result: %s", item)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
